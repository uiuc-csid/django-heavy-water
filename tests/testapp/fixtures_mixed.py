from typing import Any

from heavy_water import BaseDataBuilder
from tests.testapp.models import Record


class Succeeds(BaseDataBuilder):
    def handle(self) -> None:
        Record.objects.create(name="succeeds")


class FailsAssertion(BaseDataBuilder):
    def handle(self) -> None:
        Record.objects.create(name="fails-assertion")
        assert False, "deliberate assertion failure"


class Raises(BaseDataBuilder):
    def handle(self) -> None:
        Record.objects.create(name="raises")
        raise RuntimeError("deliberate error")


class Skipped(BaseDataBuilder):
    def should_run(self, *args: Any, **options: Any) -> bool:
        return False

    def handle(self) -> None:
        Record.objects.create(name="skipped")
