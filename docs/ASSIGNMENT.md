# Zork I LLM Agent - Assignment Documentation

## What Is This?

You have been given a Python repository that contains:
- **Zork I**: A classic text-based adventure game from 1980 (playable via `game/zork1.z3`).
- **A Z-machine Interpreter**: A Python program (`game/fic.py`) that can read and execute the Zork game file.
- **Basic Test Code**: A simple script (`test-zork.py`) showing how to run the game programmatically.

**Your mission:** Build an **LLM agent** that can play Zork by:
1. Spawning the game interpreter.
2. Reading what the game outputs (current location, game state, etc.).
3. Asking a language model (like ChatGPT via Azure) what command to execute next.
4. Sending that command to the game.
5. Logging what happens so you can see how the agent played.

This assignment challenges you to integrate AI with a classic game, handle cross-platform compatibility issues, and design a system that can be tested offline or with a real LLM.

## What Was Built

The solution implements an **LLM-driven agent** that plays Zork I by:
- **Communicating with the Zork interpreter** via pipes/pseudo-terminals using `pexpect`.
- **Querying an LLM** (Azure OpenAI chat completions endpoint) or using a mock LLM for testing.
- **Parsing game output** to extract location, score, and game state.
- **Logging interactions** in human-readable or machine-readable formats.
- **Handling cross-platform issues** so the agent works on Windows, Linux, and macOS.

## Key Challenges & How They Were Solved

### Challenge 1: Spawning Processes Across Platforms
**Problem**: The original code used `pexpect.spawn()`, which doesn't work on Windows without special setup.

**Solution**: Implement a fallback mechanism:
- Try `pexpect.spawn()` (best for Unix/Linux).
- Fall back to `pexpect.popen_spawn.PopenSpawn()` if `spawn()` isn't available (works everywhere via pipes).

### Optional Challenge 2: Terminal Control Issues on Windows
**Problem**: Zork uses the curses library for terminal control, but curses doesn't work over pipes (which is how we communicate on Windows).

**Solution**: Add a `--no-curses` mode to the interpreter:
- Detect when stdin is not a real terminal.
- Provide dummy implementations of curses that write to stdout instead.
- Game works seamlessly over pipes.

### Challenge 3: Integrating with an LLM
**Problem**: Need to ask an AI what the next move should be, but LLMs return multi-line text and may include explanations.

**Solution**:
- Send game state (location, recent output) to the LLM via HTTP request.
- Parse the response: take the first non-empty line as the command.
- Allow the LLM to include reasoning on subsequent lines (logged but not used).
- Support both real Azure endpoints and a deterministic mock LLM for offline testing.

### Challenge 4: Clear Logging & Visibility
**Problem**: Hard to understand what the agent is doing without seeing both LLM responses and game output.

**Solution**: Implement three logging modes:
1. **Plain text** (`SIMPLE_TEXT=1`): Human-friendly format showing LLM response, command, and game result.
2. **Minimal JSON** (`SIMPLE_LOG=1`): Compact JSON for programmatic analysis.
3. **Full JSON** (default): Rich context including parsed game state (room, inventory, etc.).

## How It Works: The Agent Loop

### Files You'll Interact With

| File | Role |
|------|------|
| `agent/play_with_llm.py` | **The main agent script.** This is what you run to play Zork with an LLM. |
| `game/fic.py` | **The Zork interpreter.** Modified to support `--no-curses` mode for pipe communication. |
| `game/zork1.z3` | **The game data file.** Contains the Zork I adventure. |
| `agent_run_log.txt` | **Output log (when `SIMPLE_TEXT=1`).** Shows each turn: LLM response, parsed command, and game result. |
| `agent_run_log.jsonl` | **Output log (JSON format).** Machine-readable format for analysis. |

### The Agent Loop (Step by Step)

```
1. START
   └─> Spawn: python game/fic.py game/zork1.z3 --no-curses
   └─> Read: "West of House ... Score: 0"
   
2. EACH TURN (up to MAX_TURNS times)
   ├─> Read game output (location, score, recent events)
   ├─> Build a message for the LLM:
   │   "You are at: West of House
   │    Score: 0  Turns: 0
   │    Recent output: [game text]
   │    What command next?"
   │
   ├─> Send to LLM (Azure or mock)
   │   └─> Get back: "look\nI want to see what's here."
   │
   ├─> Parse: Extract first non-empty line → "look"
   │
   ├─> Send to game: game.sendline("look")
   │
   ├─> Wait for game output:
   │   └─> Read: "You see: [objects in room]"
   │
   ├─> Log the turn:
   │   SIMPLE_TEXT:
   │     Turn 1
   │     LLM Response: look
   │     I want to see what's here.
   │     Command: look
   │     Result: You see: [objects...]
   │     ---
   │
   └─> Loop back to step 2
   
3. STOP (when MAX_TURNS reached or game ends)
   └─> Close files and exit
```

### Key Components

#### 1. **Agent Script** (`agent/play_with_llm.py`)
This is the main Python script that:
- Detects the best way to spawn the game (TTY or pipes).
- Reads game output and maintains a "rolling history" (last few lines of output).
- Sends game state to the LLM and gets back a command.
- Parses the command from potentially multi-line LLM responses.
- Sends commands to the game.
- Logs each interaction.

#### 2. **Modified Interpreter** (`game/fic.py`)
The Z-machine interpreter, enhanced with:
- A `--no-curses` flag that makes the game work over pipes.
- When detected, the interpreter uses dummy `curses` implementations instead of real terminal control.
- Output goes directly to stdout where the agent can capture it.

#### 3. **Spawn Detection** (inside `agent/play_with_llm.py`)
A fallback mechanism:
- Tries `pexpect.spawn()` first (works on Unix/Linux with PTY).
- Falls back to `pexpect.popen_spawn.PopenSpawn()` on Windows or when PTY isn't available (uses pipes).
- Automatically adds `--no-curses` when using pipe-based spawn.


### The LLM Integration: From Game State to Command

**Step 1: Extract Context**
```python
recent_output = "West of House\nYou see a mailbox.\n"
location = "West of House"
score = 0
turns = 0
```

**Step 2: Build a Message for the LLM**
```
System: "You are an agent playing Zork I. Return the command on the first line."
User: "Location: West of House
        Score: 0 Turns: 0
        Recent output: [game text]
        What command next?"
```

**Step 3: Send to LLM and Get Response**
```
LLM returns: "look\nI want to see what's around me."
```

**Step 4: Parse the Command**
```python
for line in response.splitlines():
    line = line.strip()
    if line:
        command = line  # First non-empty line
        break
# command = "look"
```

**Step 5: Send to Game**
```python
game.sendline("look")
output = game.expect('Score:')  # Wait for next game output
```

**Step 6: Log Everything**
```
Turn 1
LLM Response: look
I want to see what's around me.
Command: look
Result: You see a small mailbox here.
---
```

### Why This Design?

| Feature | Reason |
|---------|--------|
| **Multi-line LLM responses** | Allows the model to explain its reasoning; we extract just the command. |
| **Rolling history** | Gives the LLM context without overwhelming it; uses last 6 lines of game output. |
| **Multiple logging modes** | Plain text for humans, JSON for machines, VERBOSE for debugging. |
| **Mock LLM** | Test without Azure costs; reproducible results for development. |
| **Fallback spawn** | Works on any platform without special configuration. |

## Running & Testing the Agent

### Test 1: Verify Setup (30 seconds)
```powershell
python .\test-zork.py
```
This runs the original test to confirm the interpreter works. You should see game output and commands being sent.

### Test 2: Mock Agent (offline, 30 seconds)
```powershell
$env:MOCK_LLM = '1'
$env:SIMPLE_TEXT = '1'
$env:MAX_TURNS = '3'
python .\agent\play_with_llm.py
cat agent_run_log.txt
```
Fast test with deterministic fake LLM. Verify you see clear LLM responses, parsed commands, and game results.

### Test 3: Longer Mock Run (2-3 minutes)
```powershell
$env:MOCK_LLM = '1'
$env:SIMPLE_TEXT = '1'
$env:MAX_TURNS = '50'
python .\agent\play_with_llm.py
```
Longer run to see how far the mock agent progresses. Watch the score increase as it picks up items.

### Test 4: Azure LLM (if you have credentials, 5-10 minutes)
```powershell
$env:AZURE_URL = 'https://your-resource.openai.azure.com/...'
$env:AZURE_KEY = 'your-key'
$env:SIMPLE_TEXT = '1'
$env:MAX_TURNS = '20'
python .\agent\play_with_llm.py
```
Real AI playing the game. Watch how a GPT model navigates Zork—it might surprise you!

### After Each Test
Check the output:
```powershell
Get-Content agent_run_log.txt | Select -First 20  # First 20 lines
```
Or analyze with Python:
```python
import json
with open('agent_run_log.jsonl') as f:
    for line in f:
        turn = json.loads(line)
        print(f"Turn {turn['turn']}: {turn['command']} -> {turn['result'][:50]}...")
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pexpect'"
```
pip install pexpect requests
```
Install the required packages.

### "FileNotFoundError: [Errno 2] No such file or zork1.z3"
Verify files exist:
```powershell
ls game/fic.py
ls game/zork1.z3
```
If missing, check you're in the repo root directory.

### "Timeout waiting for game response"
The game didn't output within 20 seconds. Try:
1. Run `python test-zork.py` first to verify the interpreter works.
2. Increase timeout in the agent (edit `game.expect()` calls in `play_with_llm.py`).
3. Check if your system is very slow; add more time.

### "LLM call failed: [Azure error]"
Check credentials:
```powershell
$env:AZURE_URL      # Should be a full URL
$env:AZURE_KEY      # Should be a valid key
```
Test with mock first to isolate the issue:
```powershell
$env:MOCK_LLM = '1'
python .\agent\play_with_llm.py
```

### "No output files generated"
If the agent crashes before completing a turn, run with `VERBOSE`:
```powershell
$env:MOCK_LLM = '1'
$env:VERBOSE = '1'
$env:MAX_TURNS = '1'
python .\agent\play_with_llm.py
```
Console output will show where it failed.

### On Windows: "pexpect.spawn not found"
This is normal. The agent falls back to `PopenSpawn` automatically and adds `--no-curses`.
If you want to force a PTY, install `pywinpty`:
```bash
pip install pywinpty
```

## What You've Learned

After completing this assignment, you now understand:

1. **Process Management**: How to spawn and control external programs using `pexpect`.
2. **Cross-Platform Compatibility**: Fallback patterns for systems with different capabilities (TTY vs. pipes).
3. **Terminal Emulation**: Why curses doesn't work over pipes and how to provide a workaround.
4. **LLM Integration**: How to send game state to an LLM, parse responses, and extract commands.
5. **Logging & Observability**: Multiple log formats for different audiences (humans vs. machines).
6. **Game Interaction**: How to maintain state and history when interacting with interactive programs.

## Ideas for Extensions

Try implementing one of these to deepen your skills:

1. **CLI Interface**: Replace env vars with command-line arguments (`python play_with_llm.py --mock --text --turns 10`).
2. **Smart Parsing**: Extract room descriptions and inventory more accurately; use that to improve LLM prompts.
3. **Failure Recovery**: If a command fails ("You can't go that way"), tell the LLM and ask for a different command.
4. **Score Maximization**: Track the max score achieved; have the LLM optimize for that.
5. **Multi-Agent Race**: Run multiple agents with different LLM models; see which one scores higher.
6. **Web Dashboard**: Display live agent progress on a web page (rooms visited, current score, recent commands).
7. **Memory/Memory Bank**: Store facts the agent learns ("Mailbox is in West of House") and reuse them.

## References

- **Zork I**: Classic text adventure from Infocom (1980). One of the first interactive fiction games.
- **Z-Machine**: Virtual machine for running interactive fiction. [More info](https://en.wikipedia.org/wiki/Z-machine)
- **pexpect**: Python library for process interaction. [Docs](https://pexpect.readthedocs.io/)
- **Azure OpenAI**: Microsoft's hosted GPT models. [Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)



