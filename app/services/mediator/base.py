from typing import Any, Awaitable, Callable, Dict, Type


class Mediator:
    def __init__(self) -> None:
        self._commands_map: Dict[type, Callable[[Any], Awaitable[Any]]] = {}

    def register_command(self, command_type: Type, handler: Callable[[Any], Awaitable[Any]]) -> None:
        self._commands_map[command_type] = handler

    async def handle_command(self, command: Any) -> Any:
        handler = self._commands_map.get(command.__class__)
        if handler is None:
            raise RuntimeError(f"No command handler registered for {command.__class__.__name__}")
        return await handler(command)
