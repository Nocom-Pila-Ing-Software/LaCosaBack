from abc import ABC, abstractmethod
from pydantic import BaseModel


class ResponseInterface(ABC):
    @abstractmethod
    def get_response(self) -> BaseModel: raise NotImplementedError


class CreatorInterface(ABC):
    @abstractmethod
    def create(self) -> None: raise NotImplementedError


class ActionInterface(ABC):
    @abstractmethod
    def execute_action(self) -> None: raise NotImplementedError
