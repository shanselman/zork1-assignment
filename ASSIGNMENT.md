# Zork Swarm: LLM Agent Assignment

## 🎯 Objective

Build an autonomous LLM agent system that plays Zork I by querying an LLM API for decisions. Your system should:

1. **Spawn and control** the Zork game interpreter
2. **Parse game state** from text output (location, score, inventory, etc.)
3. **Query an LLM** with the current state to get the next command
4. **Execute commands** and manage the game loop
5. **Log gameplay** for analysis and debugging
6. **Handle errors** gracefully (invalid commands, game over, etc.)

## 📋 Requirements

### Core Functionality

Your implementation must:

- [ ] Launch the Zork interpreter programmatically
- [ ] Read and parse game output
- [ ] Extract key information: score, location, inventory, game state
- [ ] Query an LLM API (OpenAI-compatible) for next actions
- [ ] Send commands back to the game
- [ ] Run for a configurable number of turns (e.g., 100-500)
- [ ] Log all gameplay to files
- [ ] Handle game termination (victory, death, max turns)

### Technical Requirements

- [ ] Python 3.11+ (or your preferred language)
- [ ] Works with OpenAI API, Azure OpenAI, or vLLM
- [ ] Process management (subprocess, pexpect, etc.)
- [ ] Configurable via environment variables or CLI arguments
- [ ] Structured logging (console + files)
- [ ] Error handling and recovery

### Bonus Features (Optional)

- [ ] Docker containerization
- [ ] Multiple log formats (transcript, JSON, summary)
- [ ] Rolling context window for LLM queries
- [ ] Prompt engineering for better gameplay
- [ ] Error recovery strategies
- [ ] Real-time gameplay visualization
- [ ] Multiple game support

## 📁 What's Provided

```
zork-swarm/
├── game/
│   ├── zork1.z3          # The compiled game file
│   └── Fic/              # Z-machine interpreter (auto-cloned)
│
├── zork-source/          # Original Zork source code (reference)
│   └── *.zil files
│
├── docs/
│   └── ZORK_ACHIEVEMENT.md  # Proof the game can be beaten
│
├── play-zork.sh          # Quick launch script (Linux/Mac)
├── play-zork.ps1         # Quick launch script (Windows)
└── requirements.txt      # Basic Python dependencies
```

## 🚀 Getting Started

### 1. Test Zork

First, verify Zork works:

```bash
# Linux/Mac
./play-zork.sh

# Windows
.\play-zork.ps1
```

This runs `test-zork.py` which demonstrates using **pexpect** to control Zork programmatically.

**Install pexpect if needed:**
```bash
pip3 install --user --break-system-packages pexpect
```

Try these commands manually by modifying `test-zork.py`:
- `open mailbox`
- `read leaflet`
- `north`
- `take lamp`
- `inventory`

### 2. Understand the Approach

The `test-zork.py` script shows you how to:
- Spawn the Fic interpreter with pexpect
- Send commands to the game
- Read responses
- Detect the prompt

**This is your starting point!** Your LLM agent will work the same way, but with AI-generated commands.

**Architecture:**
- How will you spawn and control the game process?
- How will you parse the game's text output?
- How will you structure prompts to the LLM?
- How will you manage conversation context?

Choose one:

**Option A: OpenAI** (easiest, costs ~$0.30-$0.60 per game)
```bash
export OPENAI_API_KEY="sk-your-key-here"
export OPENAI_API_BASE="https://api.openai.com/v1"
export MODEL_NAME="gpt-4"
```

**Option B: vLLM** (free, self-hosted)
```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --port 8000

export OPENAI_API_BASE="http://localhost:8000/v1"
export MODEL_NAME="meta-llama/Llama-3.1-8B-Instruct"
```

### 3. Set Up Your LLM API

**Prompt Engineering:**
- What instructions should you give the LLM?
- How do you constrain output to valid commands?
- How do you provide game state context?
- How do you handle errors?

**Logging:**
- What information do you need to debug?
- How can you analyze LLM decision-making?
- What metrics matter (score, turns, completion %)?

## 🏗️ Suggested Architecture

```
┌─────────────────────────────────┐
│     Your Driver Script          │
│  (Main game loop orchestrator)  │
└──────────┬─────────┬────────────┘
           │         │
           ▼         ▼
    ┌──────────┐  ┌──────────────┐
    │   Fic    │  │  LLM Agent   │
    │  (Game)  │  │  (API calls) │
    └──────────┘  └──────────────┘
                        │
                        ▼
                  ┌──────────┐
                  │ LLM API  │
                  └──────────┘
```

**Key Components to Build:**

1. **Game Controller**
   - Spawn Fic interpreter
   - Send commands
   - Read responses
   - Detect game over

2. **Game Parser**
   - Extract score and moves
   - Identify current location
   - Parse inventory
   - Detect death/victory/errors

3. **LLM Agent**
   - Format prompts with game state
   - Query LLM API
   - Parse and clean responses
   - Manage conversation context

4. **Main Loop**
   - Coordinate all components
   - Log gameplay
   - Handle termination conditions

## 📝 Deliverables

Submit:

1. **Source code** - Your implementation
2. **README** - Setup and usage instructions
3. **Logs** - Sample gameplay logs showing:
   - At least 50 turns of gameplay
   - Score progression
   - LLM decision-making
4. **Documentation** - Brief writeup covering:
   - Architecture decisions
   - Challenges encountered
   - Prompt engineering approach
   - Results and observations

### Bonus (Optional)

- Docker setup for easy deployment
- Comparison of different models or prompts
- Analysis of LLM strategy
- Improvements beyond basic requirements

## 🎯 Evaluation Criteria

- **Functionality** (40%): Does it work? Can it play Zork autonomously?
- **Code Quality** (20%): Clean, readable, well-structured?
- **LLM Integration** (20%): Proper API usage, prompt engineering?
- **Logging/Observability** (10%): Can we see what's happening?
- **Documentation** (10%): Clear setup and explanation?

## 📚 Resources

- **Zork Commands**: https://infodoc.plover.net/manuals/zork1.pdf
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **vLLM Server**: https://docs.vllm.ai/en/latest/
- **Pexpect Docs**: https://pexpect.readthedocs.io/
- **Z-machine Spec**: https://www.inform-fiction.org/zmachine/standards/

## ❓ FAQ

**Q: Can I use a language other than Python?**  
A: Yes! But Python is recommended for easier process control.

**Q: Which LLM should I use?**  
A: GPT-4 or GPT-3.5-turbo (OpenAI) are easiest. For self-hosted, try Llama 3.1-8B or larger.

**Q: How many turns should my agent play?**  
A: Aim for 100-500 turns. Full completion takes 200+ moves, but partial gameplay is fine.

**Q: Should I implement Docker?**  
A: It's optional but recommended for bonus points.

**Q: How much will this cost with OpenAI?**  
A: ~$0.30-$0.60 per game with GPT-4, or ~$0.02-$0.05 with GPT-3.5-turbo.

---

## 🎮 Have Fun!

Remember: The goal is to learn about LLM agents, not to beat Zork perfectly. Focus on:
- Clean architecture
- Proper LLM integration
- Good observability
- Understanding how LLMs make decisions

Good luck, and may your agent explore the Great Underground Empire successfully!
