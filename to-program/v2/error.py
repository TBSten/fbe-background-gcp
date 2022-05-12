
from typing import Any, TypedDict


class ConvertException(Exception):
    def __init__(self, debugMsg: str, userMsg: str) -> None:
        super().__init__(debugMsg)
        self.debugMsg = debugMsg
        self.userMsg = userMsg


# raise unsupport(
#     ("array 1d",),
#     ("1次元配列",),
# )
def unsupport(debug: str, user: str):
    return ConvertException(
        f"{debug} is not support !",
        f"{user}はこの言語ではサポートされていないため変換できませんでした"
    )


MustBeArg = TypedDict("MustBeArg", target=str, must=str)
# raise invalid(
#     {
#         "target":"a",
#         "must":"b",
#     },
#     {
#         "target":"A",
#         "must":"B",
#     },
# )
# -> a must be b , but it is c
# -> AはBである必要があります


def mustBe(debug: MustBeArg, user: MustBeArg):
    return ConvertException(
        f'{debug["target"]} must be {debug["must"]}',
        f'{user["target"]} は{user["must"]}である必要があります'
    )


def unknown(msg: str = ""):
    return ConvertException(
        f'unknown error (msg:{msg})',
        f'不明なエラーです。',
    )


def optionMustBeFormula(formula: Any, optionName: str):
    return ConvertException(
        f"invalid formula : ${formula}",
        f"「{optionName}」オプションは計算可能な式である必要があります",
    )


def optionMustBeStr(s: Any, optionName: str):
    return ConvertException(
        f"invalid str : ${s}",
        f"「{optionName}」オプションは文字列である必要があります",
    )


def optionMustBeBool(s: Any, optionName: str):
    return ConvertException(
        f"invalid bool : ${s}",
        f"「{optionName}」オプションはYesまたはNoである必要があります",
    )
