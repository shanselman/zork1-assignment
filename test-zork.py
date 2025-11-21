#!/usr/bin/env python3
"""
Simple test script to verify Zork works with pexpect.
Use this as a reference for building your LLM agent!
"""

import sys
import os

try:
    import pexpect
except ImportError:
    print("❌ pexpect not installed!")
    print("Install with: pip3 install --user pexpect")
    sys.exit(1)

# Choose a spawn implementation. On some platforms (Windows) the
# normal pexpect.spawn may not be available; prefer it when present
# but fall back to PopenSpawn from pexpect.popen_spawn.
spawn_cls = getattr(pexpect, "spawn", None)
if spawn_cls is None:
    try:
        # PopenSpawn works on platforms without a pty (Windows)
        from pexpect import popen_spawn
        spawn_cls = popen_spawn.PopenSpawn
        print("ℹ️  pexpect.spawn not found — using pexpect.popen_spawn.PopenSpawn fallback")
    except Exception:
        print("❌ pexpect has no 'spawn' and could not import popen_spawn.")
        print("Check your pexpect installation and that you don't have a local 'pexpect' module shadowing the package.")
        print("pexpect module file:", getattr(pexpect, "__file__", None))
        sys.exit(1)

print("🎮 Testing Zork I with pexpect...")
print("=" * 60)

# Spawn the game
game_dir = os.path.join(os.path.dirname(__file__), 'game')
cmd = f'{sys.executable} {game_dir}/fic.py {game_dir}/zork1.z3'

# If we're on Windows and pexpect.spawn wasn't available at import time,
# tests will run via PopenSpawn (pipes) which doesn't provide a real PTY.
# Installing `pywinpty` makes pexpect/ptyprocess create a PTY on Windows
# so curses will work. If we're using PopenSpawn on Windows, print a hint.
try:
    from pexpect import popen_spawn
    using_popen = spawn_cls is popen_spawn.PopenSpawn
except Exception:
    using_popen = False

if os.name == 'nt' and using_popen:
    print("⚠️  On Windows and running with PopenSpawn (no PTY).")
    print("   To get a real PTY so curses works, install pywinpty:")
    print("     python -m pip install --user pywinpty pexpect")
    print("   After that, rerun this script (or use a virtualenv) so pexpect.spawn can allocate a PTY.")
game = spawn_cls(cmd, encoding='utf-8', timeout=10)

try:
    # Wait for initial output (the banner). On Windows with no-curses,
    # the game reads input via readline() which blocks, so we won't see '>'
    # until input is sent. Instead, wait for the banner text.
    game.logfile = sys.stdout  # Log game output for debugging
    game.expect('West of House', timeout=30)  # Wait for initial banner
    game.logfile = None
    print("\n[Received initial banner]")
    print("\n✅ Game started successfully!")
    print("\nUse this approach for your LLM agent:")
    print("  1. Spawn game with pexpect")
    print("  2. Send commands with game.sendline()")
    print("  3. Read responses with game.expect('>')")
    print("  4. Get output from game.before")
    print("\n" + "=" * 60)
    
    # Test command
    print("\n📝 Test: Sending 'look' command...")
    game.sendline('look')
    game.expect('West of House', timeout=5)  # Wait for response (not >, as readline blocks)
    print(game.before)
    
    # Quit
    print("\n📝 Quitting...")
    game.sendline('quit')
    try:
        game.expect(['quit', 'Goodbye', pexpect.EOF, pexpect.TIMEOUT], timeout=5)
    except pexpect.TIMEOUT:
        pass  # Game may not respond to quit; that's okay
    
    print("\n✅ Test completed! Zork is ready for your LLM agent.")
    
except pexpect.TIMEOUT:
    print("\n❌ Timeout waiting for game")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
finally:
    try:
        game.close()
    except:
        pass
