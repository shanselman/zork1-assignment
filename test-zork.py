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

print("🎮 Testing Zork I with pexpect...")
print("=" * 60)

# Spawn the game
game_dir = os.path.join(os.path.dirname(__file__), 'game')
cmd = f'python3 {game_dir}/fic.py {game_dir}/zork1.z3'
game = pexpect.spawn(cmd, encoding='utf-8', timeout=10)

try:
    # Wait for initial prompt
    game.expect('>', timeout=10)
    print(game.before)
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
    game.expect('>', timeout=5)
    print(game.before)
    
    # Quit
    print("\n📝 Quitting...")
    game.sendline('quit')
    game.expect(['quit', pexpect.EOF], timeout=5)
    
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
