from abc import ABC
from dataclasses import dataclass
from typing import List


@dataclass
class State(ABC):
    messages: List
    send: List
