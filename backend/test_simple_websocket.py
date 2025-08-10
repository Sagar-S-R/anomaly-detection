#!/usr/bin/env python3
"""
Simple WebSocket test client for the simple test server
"""
import asyncio
import websockets
import json

async def test_simple_websocket():
    """Test the simple WebSocket endpoint"""
    uri = "ws://127.0.0.1:8001/test_video"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to simple test WebSocket...")
            
            message_count = 0
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_count += 1
                    print(f"Message {message_count}: {data}")
                    
                    if "error" in data:
                        print(f"❌ Error: {data['error']}")
                        break
                    
                    # Stop after 5 messages for testing
                    if message_count >= 5:
                        print("✅ Test completed successfully!")
                        break
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON: {message}")
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("Testing simple WebSocket server...")
    asyncio.run(test_simple_websocket())
