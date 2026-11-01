from typing import Protocol


class UnitOfWork(Protocol):
    catalog: object
    stock: object
    identity: object
    media: object

    def __enter__(self): ...
    def __exit__(self, exc_type, exc_value, traceback): ...
    def commit(self) -> None: ...
    def audit(self, actor_id, action: str, resource_id=None, request_id=None) -> None: ...


class UnitOfWorkFactory(Protocol):
    def __call__(self) -> UnitOfWork: ...
