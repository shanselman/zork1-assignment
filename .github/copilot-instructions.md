**Zork1-assignment — Copilot instructions for code changes**

Purpose: give an AI coding assistant the concrete, repo-specific knowledge it needs to be productive quickly.

- **Big picture**: This repo runs the Zork I story file with a Python Z-machine interpreter (`game/fic.py`). The main developer flow is:
  - `test-zork.py` spawns the interpreter programmatically using `pexpect` and exercises commands (used as an integration test and agent reference).
  - The LLM agent should drive the interpreter the same way: spawn, wait for output, send commands, parse responses, loop.

- **Key files to read first**:
  - `test-zork.py` — canonical example of process management, spawn selection (uses `pexpect.spawn` or `pexpect.popen_spawn.PopenSpawn` fallback), and basic interactions.
  - `game/fic.py` — the interpreter. Important internals:
    - `main()` and `loop()` — program lifecycle and main interpreter loop.
    - `printToStream`, `printToCommandStream`, `writeToTextBuffer` — output paths; logging goes to `transcript.txt`, `commands.txt`, `full_log.txt`.
    - `handleInput()` / `read()` / `read_char()` — where input is consumed.
    - `Memory` class and opcode handlers — where game state (score, location, inventory buffers) lives.
  - `requirements.txt` — lists `pexpect` and other runtime deps.
  - `README.md` and `ASSIGNMENT.md` — high-level goals, quick-start, and assignment requirements.

- **Important runtime behaviors & patterns (do not change lightly)**
  - On Windows the repo provides a no-curses fallback inside `game/fic.py`. The file detects `--no-curses` or `not sys.stdin.isatty()` and replaces `curses` with a small dummy API so the interpreter can be controlled over pipes. Respect that code when editing I/O.
  - `test-zork.py` dynamically picks a spawn class: prefer `pexpect.spawn` (PTY) but fall back to `pexpect.popen_spawn.PopenSpawn` (pipes) when PTY unavailable. On Windows we recommend installing `pywinpty` so pexpect can allocate a PTY.
  - The interpreter prints a startup banner (e.g., "West of House ... Score ...") before printing `>` prompt. Agents should not assume `>` appears immediately — wait for meaningful banner text or the prompt depending on mode.
  - Output is echoed to files: `transcript.txt` (game transcript) and `commands.txt` (commands sent). Use those for test assertions and debugging.

- **Agent integration checklist (step-by-step)**
  1. Ensure environment has `pexpect` and (on Windows) `pywinpty` installed.
  2. Spawn the game using the same pattern as `test-zork.py`. Use `sys.executable` for predictable interpreter path.
  3. Read startup banner (e.g., match `West of House` or other location line) before sending the first command when running under the no-curses fallback.
  4. Parse game output for key fields: location (first line of banner), `Score:` and `Turns:` (right-justified fields in the banner), and the `>` prompt when present.
  5. Keep a rolling context window (recent N outputs + recent commands) when calling the LLM.
  6. Send the LLM-chosen action with `game.sendline()` and wait for the next response.

- **Where to put configuration & credentials**
  - Use environment variables for LLM credentials: `AZURE_ENDPOINT`, `AZURE_KEY`, `AZURE_DEPLOYMENT` (or equivalent per your Azure Foundry setup). Do not hard-code keys.

- **Testing & debug commands**
  - Manual quick test (Windows PowerShell):
    - `python .\test-zork.py`
  - If using the no-curses fallback and pipes, test logs are written to `transcript.txt` and `commands.txt` in the repo root.

- **Patterns to copy from existing code**
  - Use `game.before` after `expect()` to capture the output that triggered the match (see `test-zork.py`).
  - When spawning, use `spawn_cls = getattr(pexpect, "spawn", None)` and fallback to `popen_spawn.PopenSpawn` — keep the same detection logic.
  - Use `sys.executable` in spawn commands so the same Python interpreter is used.

- **Common pitfalls observed in this repo**
  - Importing `curses` unconditionally breaks automated testing on Windows; the repo defers/imports only when stdin is a TTY — preserve that guard.
  - Tests may block on `readline()` when agent waits for `>`; prefer waiting for the startup banner when operating over pipes.

- **If you change game I/O**
  - Update `test-zork.py` accordingly and ensure `transcript.txt` and `commands.txt` still log the same information.
  - Add a short integration test that runs `test-zork.py` in CI-like environment (recommended for future automation).

If anything above is unclear or you want the instructions expanded with examples (sample agent scaffolding that calls Azure Foundry), tell me which parts to expand and I will iterate.
