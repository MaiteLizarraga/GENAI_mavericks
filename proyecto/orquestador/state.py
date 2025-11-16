from typing_extensions import TypedDict

class UserQueryState(TypedDict):
    input: str
    model: str | None
    output: str | None
