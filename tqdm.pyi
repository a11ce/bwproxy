from typing import Any, Iterable, Iterator, TypeVar
_T = TypeVar("_T")
def tqdm(iterable: Iterable[_T], *args: Any, desc: str, unit: str, **kwargs: Any) -> Iterator[_T]: ...
def trange(*args: Any, **kwargs: Any) -> Iterator[int]: ...