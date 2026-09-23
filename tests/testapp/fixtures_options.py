from typing import Any

from heavy_water import BaseDataBuilder
from tests.testapp.models import Record


class WipeOnly(BaseDataBuilder):
    received_options: dict[str, Any] = {}

    def should_run(self, *args: Any, **options: Any) -> bool:
        WipeOnly.received_options = options
        return bool(options["wipe"])

    def handle(self) -> None:
        Record.objects.create(name="wipe-only")
