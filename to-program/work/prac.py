
from typing import Any, Callable, Dict, Literal, TypedDict, Union
from lark.visitors import Transformer
from functools import reduce

from lark.lark import Lark

from lark.tree import Tree

log_cnt = 0


def log(func: Callable):
    # def ans(*arg):
    #     global log_cnt
    #     print("   #"+str(log_cnt), func.__name__, *arg)
    #     result = func(*arg)
    #     print("   #"+str(log_cnt), "  ->", result)
    #     log_cnt += 1
    #     return result
    # return ans
    def ans(*args):
        return func(*args)
    return ans


def getGrammar():
    ans = None
    with open("./grammar.lark", encoding="utf-8") as grammarFile:
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

    def logic(self, tree):
        return tree[0]

    def bool(self, tree):
        return tree[0]

    def sum(self, tree):
        return tree[0]

    def product(self, tree):
        return tree[0]

    @log
    def add(self, tree):
        if type(tree[0]) == str or type(tree[1]) == str:
            return string_value(str(tree[0]) + str(tree[1]))
        return number_value(tree[0]+tree[1])

    @log
    def sub(self, tree):
        return number_value(tree[0] - tree[1])

    @log
    def mul(self, tree):
        return number_value(tree[0] * tree[1])

    @log
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


class TypeTransformer(CalcTransformer):
    def __init__(self, vars: Dict[str, Any] = {}) -> None:
        super().__init__(vars)

    @log
    def add(self, tree):
        if len(tree) == 1:
            return get_type(tree)
        if "string" in tree:
            return "string"
        else:
            return "number"

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
        if len(tree) == 1:
            if tree[0] == "number":
                return "number"
            else:
                raise invalidType(tree[0])
        elif tree[0] != "number":
            raise invalidType(tree[0])
        elif tree[1] != "number":
            raise invalidType(tree[1])
        return "number"

    def bool_bool_to_bool(self, tree):
        if len(tree) == 1:
            if tree[0] == "boolean":
                return "boolean"
            else:
                raise invalidType(tree[0])
        elif tree[0] != "boolean":
            raise invalidType(tree[0])
        elif tree[1] != "boolean":
            raise invalidType(tree[1])
        return "boolean"

    def to_bool(self, tree):
        return "boolean"

    def number(self, tree):
        return "number"

    def string(self, tree):
        return "string"

    def boolean(self, tree):
        print("boolean value", tree)
        return "boolean"

# text = '1+2*3+"abc"'
# text = "1+2*3+'abc'"


def eval(text):
    parser = Lark(getGrammar())
    tree = parser.parse(text)
    result = CalcTransformer().transform(tree)
    return result


def typeEval(text):
    parser = Lark(getGrammar())
    tree = parser.parse(text)
    result = TypeTransformer().transform(tree)
    return result


text = '( 2 = 3 または 1 != 4 )'
result1 = eval(text)
result2 = typeEval(text)
print("text:", text)
print("eval:", result1)
print("type:", result2)
