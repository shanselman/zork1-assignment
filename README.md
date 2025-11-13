# Zork Swarm: LLM Agent Assignment

> **🎯 Build an autonomous AI agent that plays Zork I!**
> 
> This is a programming assignment to create an LLM-powered agent that can play the classic text adventure game Zork I.
> 
> - 📋 [Assignment Instructions](docs/ASSIGNMENT.md)
> - 🎮 [Play Zork Yourself](#quick-start-play-zork) (try it first!)
> - 📚 [About Zork I](#about-zork-i)

---

## 🚀 Quick Start: Test Zork

Before building your agent, verify Zork works:

### Linux/Mac
```bash
./play-zork.sh
```

### Windows
```powershell
.\play-zork.ps1
```

This runs a simple test script (`test-zork.py`) that uses **pexpect** to control Zork programmatically. This is the same approach you'll use for your LLM agent.

**Note:** You'll need pexpect installed:
```bash
pip3 install --user --break-system-packages pexpect
```

### What You'll See
The test script will:
1. Start Zork using the Fic interpreter
2. Send a "look" command
3. Display the game response
4. Quit the game

This demonstrates the **pexpect** approach you'll use to build your LLM agent!

### Common Zork Commands
- `open mailbox` - Start your adventure
- `read leaflet` - Get helpful instructions
- `north` / `south` / `east` / `west` - Move around
- `take [item]` - Pick up an object
- `inventory` - See what you're carrying
- `look` - Describe current location
- `quit` - Exit the game

---

## 📋 Your Assignment

**Build an autonomous LLM agent that plays Zork I.**

Your system should:
1. Control the game programmatically
2. Parse game output (score, location, inventory)
3. Query an LLM API for next actions
4. Execute commands and manage the game loop
5. Log gameplay for analysis

**[📖 Read the Full Assignment](docs/ASSIGNMENT.md)**

---

## 📁 Repository Structure

```
zork-swarm/
├── game/
│   ├── zork1.z3          # The compiled game file
│   └── Fic/              # Z-machine interpreter (Python)
│
├── zork-source/          # Original Zork I source code (ZIL files)
│
├── docs/
│   ├── ASSIGNMENT.md    # 📋 START HERE - Full assignment details
│   └── ZORK_ACHIEVEMENT.md
│
├── play-zork.sh         # Quick launch (Linux/Mac)
├── play-zork.ps1        # Quick launch (Windows)
└── requirements.txt     # Python dependencies
```

---

## 🎓 About Zork I

Zork I is a 1980 interactive fiction game written by Marc Blank, Dave Lebling, Bruce Daniels and Tim Anderson and published by Infocom.

Further information on Zork I:

* [Wikipedia](https://en.wikipedia.org/wiki/Zork_I)
* [The Digital Antiquarian](https://www.filfre.net/2012/01/selling-zork/)
* [The Interactive Fiction Database](https://ifdb.tads.org/viewgame?id=0dbnusxunq7fw5ro)
* [The Infocom Gallery](http://gallery.guetech.org/zork1/zork1.html)
* [IFWiki](http://www.ifwiki.org/index.php/Zork_I)

---

## 📚 About the Source Code

This repository includes the original Zork I source code in the `zork-source/` directory.

### What is ZIL?

The source code is written in **ZIL (Zork Implementation Language)**, a dialect of MDL (Muddle), itself a dialect of LISP created by MIT students and staff.

The source code was contributed anonymously and represents a snapshot of the Infocom development system at time of shutdown.

### Compiling from Source (Optional)

The `zork-source/` directory contains the original ZIL source files. While there's no official Infocom compiler available, you can use [ZILF](http://zilf.io), a community-maintained compiler that can compile these files with minor issues.

**Note:** The compiled `game/zork1.z3` file is already provided, so compilation is optional.

---

## 📜 License & Attribution

This collection is meant for education, discussion, and historical work. The original Zork I game is © Infocom (1980).

**Fic Interpreter:** https://github.com/mjdarby/Fic  
**Original Zork Source:** https://github.com/historicalsource/zork1

Researchers are encouraged to share discoveries about this source code and the history of Infocom and its innovative employees.
