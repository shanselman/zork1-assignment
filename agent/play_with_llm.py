#!/usr/bin/env python3
"""
Simple agent to play Zork by calling an Azure OpenAI (Foundry) chat endpoint.

Configuration (environment variables):
  - AZURE_URL: Full chat completions URL, e.g.
      https://.../openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview
  - AZURE_KEY: API key for the endpoint

Usage:
  python agent/play_with_llm.py

This script is a starting point: it spawns the Fic interpreter, reads the
startup banner, queries the LLM for the next action, sends the action to the
game, and repeats for a configurable number of turns.
"""
import os
import sys
import re
import time
import json
import datetime
import requests

try:
    import pexpect
except ImportError:
    print("pexpect is required: pip install pexpect")
    raise


def get_spawn_class():
    spawn_cls = getattr(pexpect, 'spawn', None)
    using_popen = False
    if spawn_cls is None:
        # On Windows pexpect.spawn may be unavailable; fall back to PopenSpawn
        from pexpect import popen_spawn
        spawn_cls = popen_spawn.PopenSpawn
        using_popen = True
    return spawn_cls, using_popen


def parse_banner(text: str):
    # Extract a location (first non-empty line) and Score/Turns if present
    location = None
    score = None
    turns = None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if location is None:
            location = s
        m = re.search(r'Score:\s*(\d+)\s*Turns:\s*(\d+)', s)
        if m:
            score = int(m.group(1))
            turns = int(m.group(2))
    return location or '', score, turns


def parse_game_state(text: str):
    """Heuristic parser to extract room title, description, and inventory from game output.

    Returns a dict: {'room': str|None, 'description': str, 'inventory': [str,...]}
    """
    if not text:
        return {'room': None, 'description': '', 'inventory': []}

    lines = [ln.rstrip() for ln in text.splitlines()]
    # Find first meaningful line that isn't the Score/Turns banner or diagnostic
    room = None
    description_lines = []
    inventory = []

    # Skip leading empties
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    # Find room title
    for i in range(idx, len(lines)):
        s = lines[i].strip()
        if not s:
            continue
        if 'Score:' in s or 'Turns:' in s:
            continue
        if s.startswith('['):
            # e.g., diagnostic line from fic.py
            continue
        room = s
        idx = i + 1
        break

    # Gather description until blank line or inventory section or score line
    for j in range(idx, len(lines)):
        s = lines[j].rstrip()
        if not s.strip():
            break
        if 'Score:' in s or 'Turns:' in s:
            break
        low = s.lower()
        if low.startswith('you are carrying') or 'you are carrying:' in low:
            # Inline inventory after colon
            if ':' in s:
                after = s.split(':', 1)[1].strip()
                if after:
                    parts = re.split(r',|;| and ', after)
                    inventory.extend([p.strip().rstrip('.') for p in parts if p.strip()])
            # Also collect following non-empty lines as items
            k = j + 1
            while k < len(lines) and lines[k].strip():
                inventory.append(lines[k].strip().rstrip('.'))
                k += 1
            break
        description_lines.append(s)

    description = ' '.join([d for d in description_lines if d]).strip()
    return {'room': room, 'description': description, 'inventory': inventory}


def call_llm(azure_url: str, api_key: str, messages: list):
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key,
    }
    body = {
        'messages': messages,
        # Tunable parameters
        'max_tokens': 256,
        'temperature': 0.6,
    }
    resp = requests.post(azure_url, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # Expecting Azure chat-style response
    try:
        return data['choices'][0]['message']['content']
    except Exception:
        # Fallback to older shape
        return data.get('choices', [])[0].get('text')


def mock_llm_policy():
    """Return a simple cycling policy for local testing without real LLM.

    Sequence: 'look', 'north', 'take lamp', 'open mailbox', 'south'
    """
    # Provide multi-line responses to simulate an LLM that returns a short
    # explanation plus the command on a separate line. The first non-empty
    # line should be the actual command (our parser picks the first non-empty
    # line as the command).
    responses = [
        "look\nI want to see the surroundings.",
        "north\nMove toward the house to explore.",
        "take lamp\nPick up the lamp to illuminate dark rooms.",
        "open mailbox\nMaybe there's a letter inside.",
        "south\nReturn toward the southern path."
    ]
    i = 0
    while True:
        yield responses[i % len(responses)]
        i += 1


def main():
    azure_url = os.getenv('AZURE_URL')
    azure_key = os.getenv('AZURE_KEY')
    use_mock = os.getenv('MOCK_LLM', '') == '1' or (azure_key == 'MOCK')
    if not use_mock and (not azure_url or not azure_key):
        print('Please set AZURE_URL and AZURE_KEY environment variables, or set MOCK_LLM=1 for local testing')
        sys.exit(1)

    spawn_cls, using_popen = get_spawn_class()

    game_dir = os.path.join(os.path.dirname(__file__), '..', 'game')
    game_dir = os.path.abspath(game_dir)
    fic = os.path.join(game_dir, 'fic.py')
    story = os.path.join(game_dir, 'zork1.z3')

    cmd = f'{sys.executable} "{fic}" "{story}"'
    # If using PopenSpawn (pipes) force no-curses mode so the child uses stdin/stdout
    if using_popen:
        cmd = f'{sys.executable} "{fic}" "{story}" --no-curses'

    print('Spawning:', cmd)
    game = spawn_cls(cmd, encoding='utf-8', timeout=20)

    # Log transcript and commands
    transcript_f = open('transcript_agent.txt', 'a', encoding='utf-8', buffering=1)
    commands_f = open('commands_agent.txt', 'a', encoding='utf-8', buffering=1)
    jsonl_f = open('agent_run_log.jsonl', 'a', encoding='utf-8', buffering=1)
    simple_text = os.getenv('SIMPLE_TEXT', '') == '1'
    text_f = None
    if simple_text:
        text_f = open('agent_run_log.txt', 'a', encoding='utf-8', buffering=1)

    verbose = os.getenv('VERBOSE', '') == '1'
    simple_log = os.getenv('SIMPLE_LOG', '') == '1'

    # Wait for startup banner: look for the Score: field which appears in the banner
    try:
        game.expect('Score:', timeout=30)
        initial = (game.before or '') + (getattr(game, 'after', '') or '')
    except Exception:
        # If banner not clearly emitted, try reading a bit of output
        initial = game.read_nonblocking(size=4096, timeout=1) if hasattr(game, 'read_nonblocking') else (game.before or '')

    print('Initial banner:')
    print(initial)
    transcript_f.write(initial + '\n')

    # Basic system prompt for the LLM
    # Request the command on the first non-empty line and allow an optional
    # short explanation on subsequent lines. The agent will parse the first
    # non-empty line as the command and include the full raw response in logs.
    system_prompt = (
        "You are an agent that plays the text-adventure game Zork I. "
        "Each turn you will receive the current location, score, and the recent game output. "
        "Return the single game command to execute on the FIRST non-empty line. "
        "You may optionally include a short explanation on following lines. "
        "The agent will take the first non-empty line as the command and may also record any additional text as explanation."
    )

    # Rolling history to include in the prompt
    history = []
    max_turns = int(os.getenv('MAX_TURNS', '200'))

    # If mock mode, create a simple generator for deterministic commands
    mock_gen = None
    if use_mock:
        mock_gen = mock_llm_policy()

    for turn in range(1, max_turns + 1):
        # Parse most recent output to give context to the LLM
        recent = (game.before or '') + (getattr(game, 'after', '') or '')
        recent = recent.strip()
        if recent:
            transcript_f.write(recent + '\n')
            history.append(recent)
            # keep rolling window
            if len(history) > 12:
                history = history[-12:]

        location, score, turns = parse_banner('\n'.join(history[-4:]))

        # Build messages
        user_content = (
            f"Location: {location}\nScore: {score} Turns: {turns}\n\n"
            "Recent output:\n" + '\n'.join(history[-6:]) + '\n\n'
            "What single game command should the agent execute next?"
        )

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ]

        if use_mock:
            response = next(mock_gen)
        else:
            try:
                response = call_llm(azure_url, azure_key, messages)
            except Exception as e:
                print('LLM call failed:', e)
                break

        # Normalize response to a string so we can split/inspect it safely
        if response is None:
            response = ''
        else:
            try:
                response = str(response)
            except Exception:
                response = ''

        if not response:
            print('LLM returned empty response, stopping')
            break

        # LLM may return multi-line; take the first non-empty line as command
        cmd_line = None
        for ln in response.splitlines():
            ln = ln.strip()
            if ln:
                cmd_line = ln
                break

        if not cmd_line:
            print('No command parsed from LLM response; stopping')
            break

        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        print(f'[{turn}] LLM -> {cmd_line}')
        commands_f.write(cmd_line + '\n')

        # Enrich context with parsed game state
        recent_context = '\n'.join(history[-6:]) if history else ''
        state = parse_game_state(recent_context)

        # Write a pre-command JSON record with LLM response and context
        pre_record = {
            'timestamp': timestamp,
            'turn': turn,
            'phase': 'before_send',
            'llm_response_raw': response,
            'command': cmd_line,
            'location': location,
            'score': score,
            'turns': turns,
            'recent_output': recent_context,
            'room': state.get('room'),
            'room_description': state.get('description'),
            'inventory': state.get('inventory'),
            'use_mock': bool(use_mock),
        }
        # Write the pre-record when not in SIMPLE_TEXT mode
        if not simple_text:
            try:
                jsonl_f.write(json.dumps(pre_record, ensure_ascii=False) + '\n')
            except Exception:
                pass

        # Send to game (always)
        try:
            game.sendline(cmd_line)
        except Exception:
            # If sending fails, log and break
            print('Failed to send command to game')
            break

        # Wait for next output (look for Score: as a reliable marker), or EOF
        try:
            game.expect(['Score:', pexpect.EOF], timeout=20)
            out = (game.before or '') + (getattr(game, 'after', '') or '')
            if out is None:
                out = ''
            else:
                try:
                    out = str(out)
                except Exception:
                    out = ''
            print(out)
            transcript_f.write(out + '\n')

            # SIMPLE_TEXT mode: write a minimal, human-readable record with
            # both the LLM response and the game's output
            if simple_text and text_f:
                try:
                    text_f.write(f"Turn {turn}\n")
                    # LLM response (raw) may be multi-line
                    text_f.write(f"LLM Response: {response.strip()}\n")
                    text_f.write(f"Command: {cmd_line}\n")
                    text_f.write("Result:\n")
                    text_f.write(out.strip() + "\n")
                    text_f.write("---\n")
                except Exception:
                    pass

            # Non-SIMPLE_TEXT modes: write JSONL post-records as before
            if not simple_text:
                # Parse game output for richer state after the command
                post_state = parse_game_state(out)
                # If simple_log mode is enabled, write a compact record with just
                # the command and the result (game output). Otherwise write the
                # full enriched post record.
                if simple_log:
                    minimal = {
                        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                        'turn': turn,
                        'command': cmd_line,
                        'result': out,
                    }
                    try:
                        jsonl_f.write(json.dumps(minimal, ensure_ascii=False) + '\n')
                    except Exception:
                        pass
                    if verbose:
                        try:
                            print('LOG:', json.dumps(minimal, ensure_ascii=False))
                        except Exception:
                            pass
                else:
                    post_record = {
                        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                        'turn': turn,
                        'phase': 'after_recv',
                        'command': cmd_line,
                        'game_output': out,
                        'location': location,
                        'score': score,
                        'turns': turns,
                        'room': post_state.get('room'),
                        'room_description': post_state.get('description'),
                        'inventory': post_state.get('inventory'),
                    }
                    try:
                        jsonl_f.write(json.dumps(post_record, ensure_ascii=False) + '\n')
                    except Exception:
                        pass
                    if verbose:
                        try:
                            print('LOG:', json.dumps(post_record, ensure_ascii=False))
                        except Exception:
                            pass

                if isinstance(game.after, bytes) and game.after == pexpect.EOF:
                    print('Game ended (EOF)')
                    # break
        except pexpect.TIMEOUT:
            print('Timeout waiting for game response after command')
            # continue and let agent try again or exit
            # continue

    print('Agent finished')
    try:
        game.close()
    except Exception:
        pass
    try:
        jsonl_f.close()
    except Exception:
        pass
    try:
        if text_f:
            text_f.close()
    except Exception:
        pass


if __name__ == '__main__':
    main()
