from abc import ABC


class UIWidget(ABC):
    """
    Base class for all UI widgets.
    """

    def __init__(self, **kwargs):
        """
        Initialize the UI widget with optional keyword arguments.
        """
        pass

    def draw(self, *args, **kwargs):
        """
        Draw the widget. This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the __draw__ method.")
