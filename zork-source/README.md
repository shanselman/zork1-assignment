# Zork I Source Code

This directory contains the original Zork I source code written in ZIL (Zork Implementation Language).

## Files

- **zork1.zil** - Main game file
- **1actions.zil** - Action handlers
- **1dungeon.zil** - Room and object definitions
- **g*.zil** - Game engine files (parser, verbs, syntax, globals, etc.)
- **zork1.zap, zork1_data.zap, zork1_str.zap** - Compiled intermediate files

## About ZIL

ZIL (Zork Implementation Language) is a dialect of MDL (Muddle), which itself is a dialect of LISP. It was created by MIT students and staff specifically for writing interactive fiction games.

## Compiling (Optional)

The compiled game file (`../game/zork1.z3`) is already provided, but if you want to compile from source, you can use:

- **ZILF** (ZIL Compiler): http://zilf.io
  - A community-maintained compiler that can compile these files

Note: There is no official Infocom compiler publicly available. ZILF is the best modern alternative.

## Historical Context

These files represent a snapshot of the Infocom development system at the time of company shutdown. They were contributed anonymously and provide insight into how classic text adventure games were structured and programmed in the 1980s.

## For Your Assignment

You don't need to modify or compile these files. They're provided as:
- Historical reference
- Documentation of game structure
- Optional learning material about game design

Your task is to build an LLM agent that **plays** the compiled game, not to modify the game itself.
