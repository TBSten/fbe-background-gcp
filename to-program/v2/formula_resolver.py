from os import path
from typing_extensions import Self, TypedDict
from lark.lark import Lark

from typing import Any, Dict, List, Literal, Type, Union, cast
from lark.visitors import Transformer
from functools import reduce

from enum import Enum, auto

from .types import Formula
from random import random

log_cnt = 0


def getGrammar():
    ans = None
    grammar_path = path.join(
        path.dirname(__file__),
        "grammar.lark"
    )
    with open(grammar_path, encoding="utf-8") as grammarFile:
        ans = grammarFile.read()
    return ans


EvalType = Union[Literal["str"], Literal["number"], Literal["boolean"]]


def get_type(arg: Any) -> EvalType:
    if type(arg) == str:
        return "str"
    elif type(arg) == float or type(arg) == int:
        return "number"
    elif type(arg) == bool:
        return "boolean"
    else:
        raise invalidType(arg)


def invalidType(arg):
    e = TypeError(f"{arg} is invalid type : ${type(arg)}")
    return e


def number_value(arg):
    return float(arg)


def string_value(arg):
    return str(arg)


def boolean_value(arg):
    return bool(arg)


class CalcTransformer(Transformer):
    def __init__(self, vars: Dict[str, Any] = {}) -> None:
        self.vars = vars

    def expr(self, tree):
        return tree[0]

    def with_ref(self, tree):
        return tree[0]

    def logic(self, tree):
        return tree[0]

    def bool(self, tree):
        return tree[0]

    def sum(self, tree):
        return tree[0]

    def product(self, tree):
        return tree[0]

    def add(self, tree):
        if len(tree) == 1:
            return tree[0]
        if type(tree[0]) == str or type(tree[1]) == str:
            return string_value(str(tree[0]) + str(tree[1]))
        return number_value(tree[0]+tree[1])

    def sub(self, tree):
        return number_value(tree[0] - tree[1])

    def mul(self, tree):
        return number_value(tree[0] * tree[1])

    def div(self, tree):
        return number_value(tree[0] / tree[1])

    def eq(self, tree):
        return boolean_value(tree[0] == tree[1])

    def ne(self, tree):
        return boolean_value(tree[0] != tree[1])

    def lt(self, tree):
        return boolean_value(tree[0] > tree[1])

    def st(self, tree):
        return boolean_value(tree[0] < tree[1])

    def le(self, tree):
        return boolean_value(tree[0] >= tree[1])

    def se(self, tree):
        return boolean_value(tree[0] <= tree[1])

    def logic_and(self, tree):
        return boolean_value(tree[0] and tree[1])

    def logic_or(self, tree):
        return boolean_value(tree[0] or tree[1])

    def number(self, tree):
        return number_value((tree[0]))

    def string(self, tree):
        return string_value("".join(tree))

    def atom(self, tree):
        return tree[0]

    def pos(self, tree):
        return tree[0]*1

    def neg(self, tree):
        return tree[0]*-1

    def var(self, tree):
        return self.vars[tree[0]]

    def not_keyword_char(self, tree):
        print("not keyword char", tree)
        return tree[0]

#
# Types.STRING == Types.STRING()
#


class Type:
    def __init__(self, name: str, dep: Union[Type, None] = None) -> None:
        self.name = name
        self.dep = dep

    def __str__(self) -> str:
        if self.dep is None:
            return f"<{self.name}>"
        else:
            return f"<{self.name}>[{str(self.dep)}]"

    @staticmethod
    def pure(t: Type) -> Type:
        if t.dep is None:
            return t
        return Type.pure(t.dep)


class _TypesBase:
    def __init__(self) -> None:
        self.STRING: Type = Type("STRING")
        self.INTEGER: Type = Type("INTEGER")
        self.DOUBLE: Type = Type("DOUBLE")
        self.BOOLEAN: Type = Type("BOOLEAN")
        self.UNKNOWN: Type = Type("UNKNOWN")
        self._array_types: Dict[Type, Type] = {}

    def ARRAY(self, t: Type) -> Type:
        if t in self._array_types:
            return self._array_types[t]
        else:
            ans = Type("ARRAY", t)
            self._array_types[t] = ans
            return ans

    def is_array(self, t: Type) -> bool:
        return t in self._array_types.values()


# t :Type
# t == Types.STRING or
# t == Types.INTEGER or
# t == Types.DOUBLE or
# t == Types.BOOLEAN or
# t == Types.UNKNOWN or
# t == ReturnType[Types.ARRAY]
Types = _TypesBase()


class TypeTransformer(CalcTransformer):
    def __init__(self, vars: Dict[str, Any] = {}, var_types: Dict[str, Type] = {}) -> None:
        super().__init__(vars)
        self.var_types: Dict[str, Type] = var_types

    def add(self, tree):
        if Types.STRING in tree:
            return Types.STRING
        else:
            return self.num_num_to_num(tree)

    def sub(self, tree):
        return self.num_num_to_num(tree)

    def mul(self, tree):
        return self.num_num_to_num(tree)

    def div(self, tree):
        return self.num_num_to_num(tree)

    def eq(self, tree):
        return self.to_bool(tree)

    def ne(self, tree):
        return self.to_bool(tree)

    def lt(self, tree):
        return self.to_bool(tree)

    def st(self, tree):
        return self.to_bool(tree)

    def le(self, tree):
        return self.to_bool(tree)

    def se(self, tree):
        return self.to_bool(tree)

    def logic_and(self, tree):
        return self.bool_bool_to_bool(tree)

    def logic_or(self, tree):
        return self.bool_bool_to_bool(tree)

    def num_num_to_num(self, tree):
        if tree[0] == Types.UNKNOWN or tree[1] == Types.UNKNOWN:
            return Types.UNKNOWN
        if not self.is_num(tree[0]):
            raise invalidType(tree[0])
        elif not self.is_num(tree[1]):
            raise invalidType(tree[1])
        if tree[0] == Types.INTEGER and tree[1] == Types.INTEGER:
            return Types.INTEGER
        else:
            return Types.DOUBLE

    def bool_bool_to_bool(self, tree):
        if Types.UNKNOWN in tree:
            return Types.UNKNOWN
        if len(tree) == 1:
            if self.is_boolean(tree[0]):
                return Types.BOOLEAN
            else:
                raise invalidType(tree[0])
        elif tree[0] != Types.BOOLEAN:
            raise invalidType(tree[0])
        elif tree[1] != Types.BOOLEAN:
            raise invalidType(tree[1])
        return Types.BOOLEAN

    def to_bool(self, tree):
        if Types.UNKNOWN in tree:
            return Types.UNKNOWN
        return Types.BOOLEAN

    def number(self, tree):
        return tree[0]

    def double(self, tree):
        return Types.DOUBLE

    def integer(self, tree):
        return Types.INTEGER

    def string(self, tree):
        return Types.STRING

    def boolean(self, tree):
        return Types.BOOLEAN

    def is_integer(self, arg: str):
        return arg == Types.INTEGER or arg == Types.UNKNOWN

    def is_double(self, arg: str):
        return arg == Types.DOUBLE or arg == Types.UNKNOWN

    def is_num(self, arg: str):
        return arg == Types.INTEGER or arg == Types.DOUBLE or arg == Types.UNKNOWN

    def is_boolean(self, arg: str):
        return arg == Types.BOOLEAN or arg == Types.UNKNOWN

    def is_string(self, arg: str):
        return arg == Types.STRING or arg == Types.UNKNOWN

    def var(self, tree):
        print("var", *tree)
        # self.var_typesを参照して型を返す
        # ない場合はUNKNOWNを返す
        # var_name = tree[0]
        var_name = "".join(tree)
        print(
            "var", var_name, "is",
            "exists" if var_name in self.var_types else "not exists"
        )
        if var_name in self.var_types:
            print("exists var", var_name, self.var_types[var_name])
            return self.var_types[var_name]
        return Types.UNKNOWN

    def ref(self, tree):
        print("ref", *tree)
        var_name = "".join(tree[0:-1])
        print("  ", var_name)
        if var_name in self.var_types:
            return self.var_types[var_name].dep
            # return Type.pure(self.var_types[var_name])
        return Types.UNKNOWN


def resolve_value(text: Formula):
    parser = Lark(getGrammar())
    tree = parser.parse(text)
    result = CalcTransformer().transform(tree)
    return result


def resolve_type(text: Formula, variables: Dict[str, Type]):
    parser = Lark(getGrammar())
    tree = parser.parse(text)
    print(tree.pretty())
    vars: Dict[str, str] = {}
    var_types = {}
    for name in variables:
        type = variables[name]
        vars[name] = name
        var_types[name] = type
    result = TypeTransformer(vars, var_types).transform(tree)
    return result
