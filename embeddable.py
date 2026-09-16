from abc import ABC, abstractmethod


class Embeddable(ABC):
    # not really necessary for v0, but useful for future code units
    @abstractmethod
    def to_embedding_text(self) -> str:
        pass