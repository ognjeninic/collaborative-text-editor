import asyncio
import websockets
import logging

async def test_connection(uri):
    print("Attempting to connect...")
    try:
        async with websockets.connect(uri, timeout=5) as websocket:
            print("Connected successfully.")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)  # Enable detailed logging
    loop = asyncio.get_event_loop()
    loop.create_task(test_connection("ws://localhost:6789"))

    loop.run_forever()