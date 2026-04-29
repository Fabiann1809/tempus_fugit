"""
clock_memory.py — Circular Doubly Linked List for stopwatch lap storage.

ClockMemory models a clock's memory tape: each lap is a TimeRecord node
linked in both directions, and the last node wraps back to the first,
forming an endless loop — just as time itself is cyclical.

Data structure: Circular Doubly Linked List
  - Each TimeRecord holds a lap entry and two pointers (next_moment,
    previous_moment) so the list can be traversed in either direction.
  - first_record always points to the oldest (first) recorded lap.
  - When the list has one node, both its next_moment and previous_moment
    point back to itself, maintaining the circular invariant.
"""


class TimeRecord:
    """
    A single node in the ClockMemory circular doubly linked list.

    Represents one recorded lap in the stopwatch.  Each TimeRecord carries
    the lap metadata and two navigation pointers so the ring can be walked
    forward or backward from any position.

    Attributes:
        lap_number      (int):  1-based position of this lap in the session.
        elapsed_time_str (str): Human-readable elapsed time, e.g. '01:23.45'.
        timestamp       (str):  Wall-clock time when the lap was recorded,
                                e.g. '14:05:32'.
        next_moment     (TimeRecord | None): Pointer to the following node.
        previous_moment (TimeRecord | None): Pointer to the preceding node.
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
    """
    Circular Doubly Linked List that stores stopwatch lap records.

    The structure is 'circular' because the tail's next_moment always
    points back to first_record, and first_record's previous_moment always
    points to the tail.  This mirrors the cyclical nature of a clock face.

    Traversal in either direction is O(n).  Insertion and deletion at the
    tail are O(1) because we keep a direct reference to the current tail.

    Public interface (clock-domain names):
        record_moment(lap_number, elapsed_time_str, timestamp)
            Insert a new lap at the end of the ring.
        erase_moment(lap_number)
            Remove the TimeRecord with the given lap_number.
        replay_forward(from_record)
            Return the TimeRecord that comes after from_record.
        replay_backward(from_record)
            Return the TimeRecord that comes before from_record.
        all_records()
            Return a list of every TimeRecord in insertion order.
        clear()
            Remove every node and reset the list to empty.
    """

    def __init__(self):
        self.first_record: TimeRecord | None = None
        self._tail: TimeRecord | None = None
        self._size: int = 0

    # ------------------------------------------------------------------
    # Core mutation methods
    # ------------------------------------------------------------------

    def record_moment(
        self, lap_number: int, elapsed_time_str: str, timestamp: str
    ) -> TimeRecord:
        """
        Create a new TimeRecord and append it to the circular ring.

        After insertion the circular invariant is restored:
          tail.next_moment == first_record
          first_record.previous_moment == tail

        Returns the newly created TimeRecord.
        """
        node = TimeRecord(lap_number, elapsed_time_str, timestamp)

        if self.first_record is None:
            # Single-node ring: point to itself in both directions.
            node.next_moment = node
            node.previous_moment = node
            self.first_record = node
            self._tail = node
        else:
            # Attach between current tail and first_record.
            node.previous_moment = self._tail
            node.next_moment = self.first_record
            self._tail.next_moment = node          # type: ignore[union-attr]
            self.first_record.previous_moment = node
            self._tail = node

        self._size += 1
        return node

    def erase_moment(self, lap_number: int) -> bool:
        """
        Remove the TimeRecord whose lap_number matches the argument.

        Returns True if a node was removed, False if lap_number was not found.
        The circular invariant is maintained after deletion.
        """
        if self.first_record is None:
            return False

        current = self.first_record
        for _ in range(self._size):
            if current.lap_number == lap_number:
                if self._size == 1:
                    # Last node — list becomes empty.
                    self.first_record = None
                    self._tail = None
                else:
                    prev_node = current.previous_moment
                    next_node = current.next_moment
                    prev_node.next_moment = next_node   # type: ignore[union-attr]
                    next_node.previous_moment = prev_node  # type: ignore[union-attr]
                    if current is self.first_record:
                        self.first_record = next_node
                    if current is self._tail:
                        self._tail = prev_node
                self._size -= 1
                return True
            current = current.next_moment  # type: ignore[assignment]
        return False

    def clear(self) -> None:
        """Remove every TimeRecord and reset the list to its initial empty state."""
        self.first_record = None
        self._tail = None
        self._size = 0

    # ------------------------------------------------------------------
    # Traversal methods
    # ------------------------------------------------------------------

    def replay_forward(self, from_record: TimeRecord) -> TimeRecord:
        """
        Return the TimeRecord that comes after from_record in the ring.

        Because the list is circular, calling this on the last node returns
        first_record, wrapping around — like a clock hand reaching 12 again.
        """
        return from_record.next_moment  # type: ignore[return-value]

    def replay_backward(self, from_record: TimeRecord) -> TimeRecord:
        """
        Return the TimeRecord that comes before from_record in the ring.

        Wraps from first_record back to the tail on underflow.
        """
        return from_record.previous_moment  # type: ignore[return-value]

    def all_records(self) -> list[TimeRecord]:
        """Return every TimeRecord in insertion order (oldest first)."""
        if self.first_record is None:
            return []
        result: list[TimeRecord] = []
        current = self.first_record
        for _ in range(self._size):
            result.append(current)
            current = current.next_moment  # type: ignore[assignment]
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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
