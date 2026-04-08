from abc import ABC, abstractmethod
import polars as pl
from typing import Any
import logging

logger = logging.getLogger(__name__)

class MaskingRegistry:
    _strategies = {}

    @classmethod
    def register(cls, name: str, strategy_cls):
        cls._strategies[name] = strategy_cls

    @classmethod
    def get(cls, name: str):
        if name not in cls._strategies:
            raise ValueError(f"Strategy '{name}' not found")
        return cls._strategies[name]


def register_strategy(name: str):
    def decorator(cls):
        MaskingRegistry.register(name, cls)
        return cls
    return decorator


class MaskingStrategy(ABC):

    @abstractmethod
    def apply(self, value: Any, context: dict | None = None) -> Any:
        pass

    def apply_expr(self, col: pl.Expr) -> pl.Expr:
        return col.cast(pl.Utf8).map_elements(self.apply, return_dtype=pl.Utf8)