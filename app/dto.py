from pydantic import BaseModel
from typing import List, Dict, Optional, Union


class JPath(BaseModel):
    inBody: Optional[List[Dict[str, Union[str, dict]]]] = None
    inHeaders: Optional[List[Dict[str, Union[str, dict]]]] = None
    inParams: Optional[List[Dict[str, Union[str, dict]]]] = None


class Rules(BaseModel):
    allowedMethods: Optional[List[str]] = None
    jPath: Optional[JPath] = None
    regexForBody: Optional[str] = None


class ExtendedStubItem(BaseModel):
    status: int
    body: Union[dict, list] = None
    headers: Optional[dict] = None
    rules: Rules


class DefaultStubItem(BaseModel):
    status: int
    body: Union[dict, list] = None
    headers: Optional[dict] = None


class StubConfig:
    def __init__(self, default=None, list_ext=None):
        self.default: DefaultStubItem = default
        self.extended: List[ExtendedStubItem] = list_ext
