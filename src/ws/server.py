"""Server WS"""

# Libraries
import websockets
from typing import List
from datetime import datetime

from .channel import Channel
from . import MessageType
from .utils import convert_message
from .adapter import WSAdapter

class Server:
    """WS server"""
    def __init__(self, host, port, emitter: WSAdapter):
        self.host = host
        self.port = port
        self.channels: List[Channel] = []
        self.emitter = emitter

    def get_channel(self, route: str) -> Channel:
        for channel in self.channels:
            if channel.route == route:
                return channel
        return None

    def channel(self, path: str, consumer: object):
        """Create or Update consumer in channel"""
        channel_path = self.get_channel(path)
        if not channel_path:
            channel_path = Channel(path)
            self.channels.append(channel_path)
        channel_path.add_consumer(consumer)

    def remove_consumer_channel(self, path: str, consumer: object):
        channel = self.get_channel(path)
        if channel:
            channel.remove_consumer(str(consumer.id))

    async def output(self, message: dict, channel: str, message_type: MessageType, origin: str, dst: List[str] = None):
        """Send Message to Destinatary(ies)
        message: The Message to Send
        channel: The Channel to find destinataries
        dst: Destinatary(ies) -> List of users to send message if the destinatary is not in channel this ignore
        message_type: the message type is the mode of message
        """
        if message_type == message_type.UNICAST:
            if 0 <= len(dst) > 1:
                raise Exception("[Error] - Unique User not valid")
            await self.get_channel(channel).unicast(origin, dst, message)

        if message_type == message_type.BROADCAST:
            await self.get_channel(channel).broadcast(origin, message)

        if message_type == message_type.MULTICAST:
            if len(dst) < 2:
                raise Exception("[Error] - Only One User in message Multicast")
            await self.get_channel(channel).multicast(origin, dst, message)

    def start(self):
        print("---------------")
        print(f"Loading WS SERVER in {self.host}:{self.port}")
        print("---------------")
        return websockets.serve(self.handler, self.host, self.port)

    async def handler(self, websocket, path):
        self.channel(path, websocket)
        message = {
            "message": "Connected Correctly",
            "verbose_message": f"Conected to {path}",
            "channel": path,
            "timestamp": str(datetime.now().isoformat()),
            "id": str(websocket.id)
        }
        await self.output(message, path, MessageType.UNICAST, "SERVER", [str(websocket.id)])

        try:
            async for message in websocket:
                is_valid, dict_message = convert_message(message)
                if is_valid:
                    dict_message["timestamp"] = str(datetime.now().isoformat())
                    # Emit Event
                    await self.emitter.emit(str(websocket.id), self.get_channel(path), dict_message)
                else:
                    message = {"error": True, "message": "Invalid Data, is not JSON"}
                    await self.output(message, path, MessageType.UNICAST, "SERVER", [str(websocket.id)])
                    self.remove_consumer_channel(path, websocket)
        except Exception as exc:
            self.remove_consumer_channel(path, websocket)
            channel = self.get_channel(path)
            if len(channel.consumers) == 0:
                self.channels.remove(channel)
