"""Ws"""

# Libraries
from enum import Enum


class MessageType(str, Enum):
    UNICAST = "unicast"
    MULTICAST = "multicast"
    BROADCAST = "broadcast"
