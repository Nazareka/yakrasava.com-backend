from typing import Union, Tuple
from typing_extensions import Literal

TUnionRsActions = Union[
    Literal['follow'],
    Literal['unfollow'],
    Literal['make_friend'],
    Literal['unfriend'],
    Literal['make_close_friend'],
    Literal['make_relative'],
    Literal['make_beloved'],
    Literal['unmake_close_friend'],
    Literal['unmake_relative'],
    Literal['unmake_beloved']
]

TTupleRsActions = Tuple[
    Literal['follow'],
    Literal['unfollow'],
    Literal['make_friend'],
    Literal['unfriend'],
    Literal['make_close_friend'],
    Literal['make_relative'],
    Literal['make_beloved'],
    Literal['unmake_close_friend'],
    Literal['unmake_relative'],
    Literal['unmake_beloved']
]