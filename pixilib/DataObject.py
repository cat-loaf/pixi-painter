from typing import Any


class DataObject:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f"DataObject(value={self.value})"

    def __str__(self):
        return self.value.__str__()

    def __eq__(self, other):
        if isinstance(other, DataObject):
            return self.value == other.value
        return self.value == other

    def get_value(self):
        return self.value

    def set_value(self, value: Any):
        self.value = value
