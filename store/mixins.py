# store/mixins.py
from .utils.b2 import get_signed_url

class SafeURLMixin:
    def get_safe_url(self, field, default="/static/img/default.png"):
        try:
            f = getattr(self, field)
            if f and f.name:
                return get_signed_url(f.name)
        except Exception:
            pass
        return default
