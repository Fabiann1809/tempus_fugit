class TimeRecord:
    def __init__(self, lap_number: int, elapsed_time_str: str, timestamp: str):
        self.lap_number = lap_number
        self.elapsed_time_str = elapsed_time_str
        self.timestamp = timestamp
        self.next_moment: "TimeRecord | None" = None
        self.previous_moment: "TimeRecord | None" = None

    def __repr__(self) -> str:
        return (
            f"TimeRecord(lap={self.lap_number}, "
            f"time={self.elapsed_time_str}, at={self.timestamp})"
        )


class ClockMemory:
    def __init__(self):
        self.first_record: TimeRecord | None = None
        self._tail: TimeRecord | None = None
        self._size: int = 0

    def record_moment(
        self, lap_number: int, elapsed_time_str: str, timestamp: str
    ) -> TimeRecord:
        node = TimeRecord(lap_number, elapsed_time_str, timestamp)

        if self.first_record is None:
            node.next_moment = node
            node.previous_moment = node
            self.first_record = node
            self._tail = node
        else:
            node.previous_moment = self._tail
            node.next_moment = self.first_record
            self._tail.next_moment = node          # type: ignore[union-attr]
            self.first_record.previous_moment = node
            self._tail = node

        self._size += 1
        return node

    def erase_moment(self, lap_number: int) -> bool:
        if self.first_record is None:
            return False

        current = self.first_record
        for _ in range(self._size):
            if current.lap_number == lap_number:
                if self._size == 1:
                    self.first_record = None
                    self._tail = None
                else:
                    prev_node = current.previous_moment
                    next_node = current.next_moment
                    prev_node.next_moment = next_node       # type: ignore[union-attr]
                    next_node.previous_moment = prev_node   # type: ignore[union-attr]
                    if current is self.first_record:
                        self.first_record = next_node
                    if current is self._tail:
                        self._tail = prev_node
                self._size -= 1
                return True
            current = current.next_moment  # type: ignore[assignment]
        return False

    def clear(self) -> None:
        self.first_record = None
        self._tail = None
        self._size = 0

    def replay_forward(self, from_record: TimeRecord) -> TimeRecord:
        return from_record.next_moment  # type: ignore[return-value]

    def replay_backward(self, from_record: TimeRecord) -> TimeRecord:
        return from_record.previous_moment  # type: ignore[return-value]

    def all_records(self) -> list[TimeRecord]:
        if self.first_record is None:
            return []
        result: list[TimeRecord] = []
        current = self.first_record
        for _ in range(self._size):
            result.append(current)
            current = current.next_moment  # type: ignore[assignment]
        return result

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __repr__(self) -> str:
        records = self.all_records()
        chain = " ⟺ ".join(str(r.lap_number) for r in records)
        if records:
            chain = f"[{chain}] (circular)"
        return f"ClockMemory(size={self._size}, ring={chain or 'empty'})"
