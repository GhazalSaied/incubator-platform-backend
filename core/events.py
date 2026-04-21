from core.catalog import EVENTS


class EventBus:
    _listeners = {}

    # ----------------------------------

    @classmethod
    def register(cls, event_name, handler):
        cls._listeners.setdefault(event_name, []).append(handler)

    # ----------------------------------

    @classmethod
    def emit(cls, event_name, **kwargs):
        """
        Smart Emit:
        - يتحقق من event catalog
        - يضيف action_url تلقائي
        - يبعت payload موحد لل handlers
        """

        if event_name not in EVENTS:
            raise Exception(f"Event '{event_name}' not defined in catalog")

        event_config = EVENTS[event_name]

        #  بناء action_url تلقائي
        action_url = cls._build_action_url(event_config, kwargs)

        #  تجهيز payload موحد
        payload = {
            **kwargs,
            "event_name": event_name,
            "action_url": action_url,
            "target": event_config.get("target"),
        }

        #  استدعاء handlers
        for handler in cls._listeners.get(event_name, []):
            handler(payload)

    # ----------------------------------

    @staticmethod
    def _build_action_url(event_config, data):
        """
        يبني action_url من catalog + payload
        """

        template = event_config.get("action_url")

        if not template:
            return None

        try:
            return template.format(**EventBus._extract_ids(data))
        except Exception:
            return template

    # ----------------------------------

    @staticmethod
    def _extract_ids(data):
        """
        يحول objects → ids لاستخدامها بالـ URL
        """

        extracted = {}

        for key, value in data.items():
            if hasattr(value, "id"):
                extracted[key] = value.id

        return extracted