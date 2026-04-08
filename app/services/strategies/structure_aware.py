import polars as pl
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
    
    def apply_expr(self, col: pl.Expr) -> pl.Expr:
        p, q = self.p, self.q
        col = col.cast(pl.Utf8)
        n = col.str.len_chars()
        mask_len = (n - p - q)


        prefix = col.str.slice(0, p)
        mask = pl.lit("*").repeat_by(mask_len).list.join("")
        suffix = pl.when(q > 0).then(col.str.slice(-q)).otherwise(pl.lit(""))

        return (
            pl.when(n > p + q)
            .then(pl.concat_str([prefix, mask, suffix]))
            .otherwise(col)
            .cast(pl.Utf8)
        )
    

    