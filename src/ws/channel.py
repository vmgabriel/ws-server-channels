"""Load Channels configuration"""

# Libraries
from typing import List

from .utils import convert_to_message


class Channel:
    """Channel for each route"""
    def __init__(self, route: str):
        self.route: str = route
        self.consumers = {}

    def add_consumer(self, consumer: object):
        """Add a new consumer
        the consumer is dict as object.consumer
        """
        id = str(consumer.id)
        if id not in self.consumers:
            self.consumers[id] = consumer

    def get_consumer(self, id: str) -> object:
        """Get consumer with id"""
        return self.consumers.get(id, None)

    def remove_consumer(self, id: str) -> object:
        """Remove Consumer Based in id"""
        consumer = self.consumers.get(id, None)
        if consumer:
            del self.consumers[id]
        return consumer

    async def unicast(self, origin: str, id_consumer: str, message: dict):
        """Send Message to unique user with id_consumer"""
        message["origin"] = origin
        consumer = self.get_consumer(id_consumer[0])
        await consumer.send(convert_to_message(message))

    async def multicast(self, origin: str, id_consumers: List[str], message: dict):
        """Send Message to specific users"""
        for id_consumer in id_consumers:
            await self.unicast(origin, id_consumer, message)

    async def broadcast(self, origin: str, message: dict):
        """Send Message to All consumers of Channel"""
        message["origin"] = origin
        print("consumers - ", self.consumers)
        for id, consumer in self.consumers.items():
            await consumer.send(convert_to_message(message))

    def __str__(self):
        return f"Channel {self.route} - consumers: {self.consumers}"

    def __repr__(self):
        return str(self)
