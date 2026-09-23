from heavy_water import BaseDataBuilder
from tests.testapp.models import Record


class Basic(BaseDataBuilder):
    def handle(self) -> None:
        Record.objects.create(name="basic")
