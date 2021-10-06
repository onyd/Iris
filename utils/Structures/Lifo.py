from typing import Iterable


class Cell:
    def __init__(self, value, next=None, priority=0):
        self.value = value
        self.next = next

        self.priority = priority

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class LifoIterator:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current:
            current = self.current
            self.current = self.current.next
            return current.value
        else:
            raise StopIteration


class Lifo(Iterable):
    def __init__(self, head=None):
        self.head = head

        self._length = 0

    @classmethod
    def from_list(cls, list):
        cell = None
        _length = len(list)
        for i in range(len(list) - 1, -1, -1):
            cell = Cell(list[i], cell)

        L = cls(cell)
        L._length = _length
        return L

    def __str__(self):
        string = ""
        for x in self:
            string += f"{str(x)}->"

        return string[:-2]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self._length

    def __contains__(self, key):
        current = self.head
        while current:
            if current.value == key:
                return True
            current = current.next

        return False

    def __iter__(self):
        return LifoIterator(self.head)

    def empty(self):
        return len(self) == 0

    def clear(self):
        self.head = None
        self._length = 0

    def push(self, *args):
        for elt in args:
            self.head = Cell(elt, self.head)
            self._length += 1

    def pop(self):
        if not self.empty():
            elt = self.head
            self.head = self.head.next
            self._length -= 1
            return elt

    def insert(self, elt, priority):
        prev = None
        current = self.head
        while current and current.priority > priority:
            prev, current = current, current.next

        new = Cell(elt, current)
        if prev:
            prev.next = new
        else:
            self.head = new

        self._length += 1

    def remove_all(self, priority):
        prev = None
        current = self.head
        while current:
            if current.priority == priority:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
            prev, current = current, current.next
