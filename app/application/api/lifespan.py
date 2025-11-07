from contextlib import asynccontextmanager


@asynccontextmanager
def lifespan(*_):
    try:
        yield
    finally:
        ...
