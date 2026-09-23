from typing import Any

from heavy_water import BaseDataBuilder
from tests.testapp.models import Record


class BrokenInit(BaseDataBuilder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("deliberate init error")

    def handle(self) -> None:
        Record.objects.create(name="broken-init")
