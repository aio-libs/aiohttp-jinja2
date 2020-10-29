from typing import Callable, Union, Iterable, Tuple, Mapping

Filter = Callable[..., str]
Filters = Union[Iterable[Tuple[str, Filter]], Mapping[str, Filter]]
