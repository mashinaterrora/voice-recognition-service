from contextlib import asynccontextmanager
from typing import Generic, Protocol, Type, TypeVar

ModelT = TypeVar("ModelT")
GatewayT = TypeVar("GatewayT")


class UoWPort(Protocol):
    def register_dirty(self, model: ModelT) -> None:
        raise NotImplementedError

    def register_deleted(self, model: ModelT) -> None:
        raise NotImplementedError

    def register_new(self, model: ModelT) -> "UoWModel[ModelT]":
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def register_repository(self, model_class: Type[ModelT], repository: GatewayT) -> None:
        raise NotImplementedError

    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
            await self.commit()
        except Exception as exc:
            await self.rollback()
            raise exc


class UoWModel(Generic[ModelT]):
    def __init__(self, model: ModelT, uow):
        self.__dict__["_model"] = model
        self.__dict__["_uow"] = uow

    def __getattr__(self, key: str):
        return getattr(self._model, key)

    def __setattr__(self, key: str, value):
        setattr(self._model, key, value)
        self._uow.register_dirty(self._model)
