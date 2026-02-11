"""Test send_and_wait to see if auth works and we get a response."""

import asyncio
from copilot import CopilotClient


async def main():
    client = CopilotClient()
    await client.start()
    print("Client started")

    session = await client.create_session({"model": "gpt-4.1"})
    print("Session created")

    result = await session.send_and_wait({"prompt": "Say hello"}, timeout=20000)
    print(f"RESULT type: {type(result)}")
    print(f"RESULT: {result}")
    if result and hasattr(result, "data"):
        print(f"CONTENT: {result.data.content}")
    else:
        print("No result returned")

    await session.destroy()
    await client.stop()
    print("Done")


asyncio.run(main())
