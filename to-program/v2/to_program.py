

import traceback
from typing import Generic, TypeVar
from v2.error import ConvertException
from v2.lang.java import JavaConverter
from v2.lang.javascript import JavaScriptConverter
from v2.lang.python import PythonConverter
from v2.types import FBEFormat

T = TypeVar("T")


class Test(Generic[T]):
    def set(self, v: T):
        self.value: T = v

    def get(self) -> T:
        return self.value


langs: dict = {
    "javascript": JavaScriptConverter,
    "python": PythonConverter,
    "java": JavaConverter,
}


def to_program(fbe: FBEFormat, target: str):
    if target in langs:
        try:
            # print(target)
            result = langs[target](fbe).convert()
            # print(result)
            return {
                "result": result,
            }
        except ConvertException as e:
            print("convert exception")
            print(traceback.format_exc())
            return {
                "error": e.__str__(),
                "details": e.userMsg,
            }
        except Exception as e:
            print(traceback.format_exc())
            return {
                "error": e.__str__(),
            }
    else:
        return {
            "msg": "error",
            "error": f"invalid target : {target}"
        }
