from abc import ABC, abstractmethod


class Transaction(ABC):
    @classmethod
    @abstractmethod
    def check_condition(cls, state):
        pass

    @classmethod
    @abstractmethod
    def action(cls, state):
        pass
