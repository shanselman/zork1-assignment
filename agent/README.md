# Zork Agent

This folder contains `play_with_llm.py`, a simple agent that spawns the Zork I
interpreter and asks an LLM what command to send next.

Quick start (local, mock LLM):

PowerShell:
```
$env:MOCK_LLM = '1'
python .\agent\play_with_llm.py
```

To use a real Azure OpenAI / Foundry endpoint set:

```
$env:AZURE_URL = 'https://<your-host>/openai/deployments/<deployment>/chat/completions?api-version=2025-01-01-preview'
$env:AZURE_KEY = '<your-key>'
python .\agent\play_with_llm.py
```

Logs written to `transcript_agent.txt` and `commands_agent.txt` in the repo root.

Per-turn JSON logging
 - The agent now writes per-turn JSON lines to `agent_run_log.jsonl` (append mode).
 - Each turn produces at least one record before sending the command and one after receiving the game's output.
 - Fields include `timestamp`, `turn`, `phase` (before_send/after_recv), `command`, `llm_response_raw`, `game_output`, `location`, `score`, and `turns`.

Additional parsed state
 - The agent attempts to heuristically parse each turn's recent output and includes:
	 - `room`: the parsed room title (first meaningful line)
	 - `room_description`: a short concatenated description paragraph
	 - `inventory`: array of inventory items if the game printed "You are carrying" or equivalent

	Simple minimal logging
	 - Set environment variable `SIMPLE_LOG=1` to produce minimal JSONL records in `agent_run_log.jsonl`.
	 - Each record will contain only: `timestamp`, `turn`, `command`, and `result` (the game's output for that command).

	Plain-text minimal logging
	 - Set environment variable `SIMPLE_TEXT=1` to produce plain-text minimal records in `agent_run_log.txt`.
	 - Each record will be appended as:
		 Turn <n>
		 Command: <command string>
		 Result:
		 <raw game output>
		 ---

