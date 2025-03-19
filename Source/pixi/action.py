class Action:
    def __init__(self, function:callable, args, kwargs, undo:callable):
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
        return self.function(*args, **kwds)

    def redo(self):
        return self.function(*self.args, **self.kwargs) 
    
    def undo(self):
        try:
            return self._undo(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
            return None
    