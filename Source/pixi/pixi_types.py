class Vec2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if not isinstance(other, Vec2D):
            raise TypeError(f"Cannot add Vec2D and {type(other)}")
        return Vec2D(self.x+other.x, self.y+other.y)

