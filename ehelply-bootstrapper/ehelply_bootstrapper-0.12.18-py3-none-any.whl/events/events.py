from typing import Dict, List, Union
from pydantic import BaseModel


class Event(BaseModel):
    """
    The Event class represents some event that is triggered.

    This class is a BASE CLASS and is MEANT to be overridden. Create a new Event class based on this one for each
        type of event.
    """
    name: str


class EventResponse(BaseModel):
    """
    EventResponse is a class that represents a response from an EventListener. This shouldn't be overridden.
    """
    name: str
    parameters: dict = {}


class EventListener:
    """
    EventListener handles triggered events.

    You should override this class and create a new class based on this class for EACH event type that can be triggered.

    Return EventResponses for what the Controller should do as a result of the event.
    The EventResponse name is the function to call on the controller. And the EventResponse parameters are the values
        to pass to the function.
    """
    def __init__(self, event_name: str, event_model):
        self.event_name = event_name
        self.event_model = event_model

    def verify(self, event: Event) -> bool:
        """
        Verifies that an incoming event matches the event model that this listener is expecting.

        DON'T OVERRIDE
        """
        if isinstance(event, self.event_model):
            return True
        return False

    def trigger(self, event: Event) -> Union[None, List[EventResponse]]:
        """
        Event handler function

        MUST BE OVERRIDEN
        """
        pass


class EventController:
    """
    EventController will register n listeners.

    Then, when an Event is triggered, it will run through the listeners in order. Each Listener will return a list of
        EventResponses. These EventResponses then trigger a function on the controller
    """
    def __init__(self):
        self.listeners: Dict[str, List[EventListener]] = {}

    def register_listener(self, listener: EventListener):
        """
        Register a new EventListener
        """
        if listener.event_name in self.listeners:
            self.listeners[listener.event_name].append(listener)
        else:
            self.listeners[listener.event_name] = [listener]

    def trigger(self, event: Event):
        """
        Trigger a new Event

        Loops through all of the EventListeners that are registered to listen to that event name in order.

        Then, after each EventListener is processed, it will trigger the EventResponses
        """
        for listener in self.listeners[event.name]:
            if listener.verify(event):
                event_responses = listener.trigger(event)
                if event_responses:
                    for response in event_responses:
                        getattr(self, response.name)(**response.parameters)
