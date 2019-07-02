from abc import ABC, abstractmethod


class Pricer(ABC):

    def __init__(self):
        self.cache = {}

    @abstractmethod
    def price(self):
        pass
