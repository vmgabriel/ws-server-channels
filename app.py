"""Server WS"""

# Libraries
import os
import asyncio

# Modules
from src.ws.server import Server
from src.config import HOST, PORT
from src.ws.adapter import WSAdapter, EventWS


class EventPlay(EventWS):
    def __init__(self):
        self._event_title = "PLAY"

    async def event(self, origin: str, channel, message: dict):
        message["res"] = "Ejecutado evento emitter"
        print("message - ", message)
        print("ws - ", origin)
        await channel.broadcast(origin, message)


if __name__ == "__main__":
    ws_event = WSAdapter()
    event_play = EventPlay()
    ws_event.add_event(event_play)
    ws = Server(HOST, PORT, ws_event)

    asyncio.get_event_loop().run_until_complete(ws.start())
    asyncio.get_event_loop().run_forever()
