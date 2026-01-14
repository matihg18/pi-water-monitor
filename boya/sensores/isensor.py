from abc import ABC, abstractmethod

class ISensor(ABC):
    @abstractmethod
    def read(self) -> dict:

        pass

