from abc import ABC, abstractmethod

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
    def apply(self, value: str) -> str:
        pass