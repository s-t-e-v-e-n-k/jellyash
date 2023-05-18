import sys
from typing import Dict, Iterator, Union

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:
    from typing_extensions import Self

from jellyfin_apiclient_python.api import API


class Item:
    def __init__(self, item: Dict[str, str]):
        self.item = item

    def _raw_item(self) -> Dict[str, str]:
        return self.item

    def __getattr__(self, attr: str) -> Union[str, Self]:
        try:
            value = self.item[attr]
            if isinstance(value, dict):
                value = Item(value)
            return value
        except KeyError:
            raise AttributeError(f"Item has no attribute '{attr}'")


class ApiResponse:
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return f"<ApiResponse object containing {len(self)} items>"

    def __iter__(self) -> Iterator[Item]:
        yield from [Item(i) for i in self.value["Items"]]

    def __getitem__(self, key) -> Item:
        return Item(self.value["Items"][key])

    def _raw_value(self):
        return self.value

    def __len__(self) -> int:
        return self.value["TotalRecordCount"] + self.value["StartIndex"]


class WrappedAPI(API):
    def _get(self, handler, params=None):
        return ApiResponse(super()._get(handler, params=params))

