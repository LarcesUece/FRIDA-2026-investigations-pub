from app.services.strategies.base import MaskingStrategy, register_strategy


@register_strategy("structure_aware")
class StructureAwareMasking(MaskingStrategy):

    def __init__(self, p: int, q: int):
        self.p = p
        self.q = q

    def apply(self, value: str) -> str:
        if value is None or value == "":
            return value

        n = len(value)

        if self.p + self.q >= n:
            return value

        return value[:self.p] + "*" * (n - self.p - self.q) + value[-self.q:]