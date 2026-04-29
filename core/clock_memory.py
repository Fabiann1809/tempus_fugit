"""
Circular Doubly Linked List for stopwatch lap storage.

Each lap is a TimeRecord node linked forward and backward.
The tail's next_moment always points to first_record, and
first_record's previous_moment always points to the tail.
Insertion/deletion at the tail: O(1). Traversal: O(n).
"""


class TimeRecord:
    """
    Single node in the ClockMemory ring.

    Attributes:
        lap_number       (int): 1-based lap index.
        elapsed_time_str (str): Formatted elapsed time, e.g. '01:23.45'.
        timestamp        (str): Wall-clock time of recording, e.g. '14:05:32'.
        next_moment      (TimeRecord | None): Next node in the ring.
        previous_moment  (TimeRecord | None): Previous node in the ring.
    """

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
    """Circular Doubly Linked List that stores stopwatch lap records."""

    def __init__(self):
        self.first_record: TimeRecord | None = None
        self._tail: TimeRecord | None = None
        self._size: int = 0

    def record_moment(
        self, lap_number: int, elapsed_time_str: str, timestamp: str
    ) -> TimeRecord:
        """Append a new TimeRecord to the ring, restoring the circular invariant."""
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
        """Remove the node with the given lap_number. Returns True if found."""
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
        """Remove every node and reset to empty."""
        self.first_record = None
        self._tail = None
        self._size = 0

    def replay_forward(self, from_record: TimeRecord) -> TimeRecord:
        """Return the next node; wraps from tail back to first_record."""
        return from_record.next_moment  # type: ignore[return-value]

    def replay_backward(self, from_record: TimeRecord) -> TimeRecord:
        """Return the previous node; wraps from first_record back to tail."""
        return from_record.previous_moment  # type: ignore[return-value]

    def all_records(self) -> list[TimeRecord]:
        """Return all nodes in insertion order."""
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
