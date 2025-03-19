from .pixi_types import Vec2D
class Action:
    def __init__(self, function: callable, args, kwargs, undo: callable):
        """
        Initialize an Action object.
        Args:
            function (callable): The function to be executed.
            args (tuple): The positional arguments to pass to the function.
            kwargs (dict): The keyword arguments to pass to the function.
            undo (callable): The function that undos the action.
        """
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._undo = undo

    def __call__(self, *args, **kwds):
        pass

    def redo(self):
        pass

    def undo(self):
        pass

class CanvasPaintCellAction(Action):
    def __init__(self, canvas, location : Vec2D, colour):
        self.canvas = canvas
        self.location = location
        self.colour = colour
        self.old_colour = None
    
    def run(self):
        self.old_colour = self.canvas.getCellColour(self.location)
        self.canvas.paintCell(self.location, self.colour)
    
    def undo(self):
        self.canvas.paintCell(self.location, self.old_colour)
    
class CanvasFillAction(Action):
    def __init__(self, canvas, origin : Vec2D, colour):
        ...
        #  hold on
        #  doesn't passing args pass by copy instead of reference in python