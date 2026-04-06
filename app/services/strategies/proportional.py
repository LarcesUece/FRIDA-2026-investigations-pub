import math
from app.services.strategies.base import MaskingStrategy, register_strategy


@register_strategy("proportional")
class ProportionalMasking(MaskingStrategy):

    def __init__(self, alpha: float):
        self.alpha = alpha

    def apply(self, value: str) -> str:
        if value is None or value == "":
            return value

        n = len(value)
        k = math.ceil(self.alpha * n)

        return value[:k] + "*" * (n - k)