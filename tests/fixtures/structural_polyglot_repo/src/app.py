import os
from pathlib import Path


class ExampleService:
    def compute(self, value):
        return value


def public_entry(name, base=1):
    return f"{name}:{base}"
