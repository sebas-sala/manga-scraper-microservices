"""Base class for all services"""

from abc import abstractmethod

class Base:
    """Base class for all services"""

    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @abstractmethod
    def on_message(self, body):
        """Process a message"""
