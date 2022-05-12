
from typing import Dict
from pprint import pprint


class T:
    def __init__(self, name: str, *deps) -> None:
        self.name = name
        self.deps: T = deps  # type: ignore

    def __str__(self) -> str:
        return f"<{self.name}>"


class _TypesBase:
    def __init__(self) -> None:
        self.STRING = T("STRING")
        self.NUMBER = T("NUMBER")
        self.BOOLEAN = T("BOOLEAN")
        self._arrays: Dict[T, T] = {}

    def ARRAY(self, t: T):
        if t in self._arrays:
            return self._arrays[t]
        else:
            ans = T("ARRAY-"+str(t), t)
            self._arrays[t] = ans
            return ans

    def is_array(self, t: T):
        return t in self._arrays.values()


Types = _TypesBase()
ARRAY = Types.ARRAY


ts = [
    Types.STRING,
    Types.NUMBER,
    Types.BOOLEAN,
    ARRAY(Types.STRING),
    ARRAY(Types.NUMBER),
    ARRAY(Types.BOOLEAN),
    ARRAY(ARRAY(Types.STRING)),
    ARRAY(ARRAY(Types.NUMBER)),
    ARRAY(ARRAY(Types.BOOLEAN)),
    ARRAY(ARRAY(ARRAY(Types.BOOLEAN))),
    ARRAY(ARRAY(ARRAY(ARRAY(Types.BOOLEAN)))),
]
for t in ts:
    print(t, Types.is_array(t))
