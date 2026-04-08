import math
from app.services.strategies.base import MaskingStrategy, register_strategy
import polars as pl

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
    
    def apply_expr(self, col: pl.Expr) -> pl.Expr:
        col = col.cast(pl.Utf8)
        n = col.str.len_chars()
        k = (n * self.alpha).ceil().cast(pl.Int64)

        prefix = col.str.slice(0, k)
        mask_len = n - k
        mask = pl.lit("*").repeat_by(mask_len).list.join("")

        return pl.concat_str([prefix, mask])