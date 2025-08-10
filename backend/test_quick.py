#!/usr/bin/env python3
"""
Quick WebSocket test with timeout and better error handling
"""

import asyncio
import websockets
import json
import signal
import sys

async def test_websocket():
    uri = "ws://127.0.0.1:8000/stream_video"
    timeout = 30  # 30 seconds timeout
    
    try:
        print("Connecting to WebSocket...")
        async with websockets.connect(uri, timeout=5) as websocket:
            print("✅ Connected successfully!")
            
            # Receive a few messages
            for i in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(message)
                    print(f"Message {i+1}: {data.get('status', 'Unknown')}")
                    
                    if 'error' in data:
                        print(f"⚠️  Server error: {data['error']}")
                    
                except asyncio.TimeoutError:
                    print(f"⏰ Timeout waiting for message {i+1}")
                    break
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"Raw message: {message}")
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print("✅ Test completed successfully!")
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the server running?")
    except websockets.exceptions.InvalidURI:
        print("❌ Invalid WebSocket URI")
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def signal_handler(sig, frame):
    print("\n🛑 Test interrupted by user")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    print("🧪 Quick WebSocket Test")
    print("Press Ctrl+C to stop")
    print("=" * 30)
    
    asyncio.run(test_websocket())
