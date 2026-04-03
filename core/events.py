class EventBus:

    _listeners = {}

    @classmethod
    def register(cls, event_name, handler):
        cls._listeners.setdefault(event_name, []).append(handler)

    @classmethod
    def emit(cls, event_name, **kwargs):
        for handler in cls._listeners.get(event_name, []):
            handler(**kwargs)