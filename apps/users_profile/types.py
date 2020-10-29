from __future__ import annotations

from typing import Dict, Tuple, Sequence, NewType, Union, Tuple, List, TypedDict, Literal

from rest_framework.utils.serializer_helpers import ReturnDict
# from mypy_extensions import TypedDict
 

TStatus = Union[
    Literal['online'], 
    Literal['offline']
]
TSex = Union[
    Tuple[
        Literal['ML'], 
        Literal['Male']
    ],
    Tuple[
        Literal['FM'], 
        Literal['Female']
    ],
    Tuple[
        Literal['OT'], 
        Literal['other']
    ]
]
TRelated = Union[
    Literal['none'], 
    Literal['from'], 
    Literal['to']
]

class TShortProfile(TypedDict): 
    id: int
    nickname: str
    image: str
    status: TStatus


class TFullProfile(TypedDict): 
    id: int
    nickname: str
    location: str
    date_of_birth: str
    sex: TSex
    status: TStatus
    main_quote: str
    profession: str
    image: str

class TFullProfileWithStatus(TypedDict):
    profile: ReturnDict
    related: TRelated
    status: TStatus
