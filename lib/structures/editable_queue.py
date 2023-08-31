from asyncio import Queue
from typing import Any, Callable, Generic, Self, TypeVar

T = TypeVar("T")


class QueueItem(Generic[T]):
    def __init__(self: Self, value: T):
        self.value = value
        self.skip = False


class EditableQueue(Generic[T]):
    def __init__(self: Self, maxsize: int = 0):
        self._queue: Queue[QueueItem[T]] = Queue(maxsize)

    async def put(self: Self, item: T) -> None:
        await self._queue.put(QueueItem(item))

    async def get(self: Self) -> T:
        while True:
            item = await self._queue.get()

            if item.skip:
                continue

            return item.value

    def remove(self: Self, callback: Callable[[Any], bool]) -> int:
        count = 0
        for item in self._queue._queue:
            skip = callback(item.value)

            item.skip = skip

            if skip:
                count += 1

        return count

    def task_done(self) -> None:
        self._queue.task_done()
