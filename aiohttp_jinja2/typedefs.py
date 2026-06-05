from typing import Callable, Iterable, Mapping

Filter = Callable[..., str]
Filters = Iterable[tuple[str, Filter]] | Mapping[str, Filter]
