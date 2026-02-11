"""Quick diagnostic: inspect event objects from the Copilot SDK."""

import asyncio
from copilot import CopilotClient


async def main():
    client = CopilotClient()
    await client.start()
    session = await client.create_session({"model": "gpt-4.1", "streaming": True})

    done = asyncio.Event()

    def on_event(event):
        etype = event.type
        has_value = hasattr(etype, "value")
        print(f"EVENT  type={etype!r}  type_type={type(etype).__name__}  has_value={has_value}")
        if has_value:
            print(f"       value={etype.value!r}")
        if hasattr(event, "data") and event.data is not None:
            attrs = [a for a in dir(event.data) if not a.startswith("_")]
            print(f"       data attrs={attrs}")
            if hasattr(event.data, "delta_content"):
                print(f"       delta_content={event.data.delta_content!r}")
            if hasattr(event.data, "content"):
                c = event.data.content
                print(f"       content={c[:100]!r}" if c else "       content=None")
        etype_str = etype.value if has_value else str(etype)
        if etype_str == "session.idle":
            done.set()

    session.on(on_event)
    await session.send({"prompt": "Say hello in one word"})
    await asyncio.wait_for(done.wait(), timeout=30)
    await session.destroy()
    await client.stop()


asyncio.run(main())
