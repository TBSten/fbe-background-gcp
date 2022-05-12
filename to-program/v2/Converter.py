from os import replace
from typing import Any, Dict, List, Type, TypeVar, TypedDict,  cast

from v2.types import FBEFormat, Flow, Formula, Item, ItemId, Formula, Sym, get_option_value, get_option_value_as_bool, get_option_value_as_formula, get_option_value_as_str, is_flow, is_item, is_sym

import re


def item_one_line(func):
    def deco_func(self, *args) -> str:
        content = func(self, *args)
        return self.line(content)
    return deco_func


Variables = Dict[
    str,            # フローチャート内の変数名
    str             # プログラム内のidentifier
]


class Converter:
    def __init__(self, fbe: FBEFormat) -> None:
        self.items = fbe["items"]
        self.flowIds = fbe["meta"]["flowIds"]
        self.title = fbe["meta"]["title"]
        self.variables: Variables = {}
        self.indent = 0
        self.indent_str: str = "    "

    def convert(self) -> str:
        builder = CodeBuilder("")
        flows = self.get_flows(self.flowIds)
        for flow in flows:
            builder.add(
                self.flow(
                    flow,
                    flow["childrenItemIds"],
                    True,
                    flow["tag"]
                )
            )
        return builder.get()

    # ユーティリティ
    def get_item(self, item_id: ItemId):
        matches = list(
            filter(lambda item: item["itemId"] == item_id, self.items))
        if len(matches) <= 0:
            raise not_exists_item_error(item_id)
        if len(matches) >= 2:
            raise multi_exists_item_error(item_id)
        return matches[0]

    def get_items(self, item_ids: List[ItemId]):
        ans: List[Item] = []
        for id in item_ids:
            item = self.get_item(id)
            ans.append(item)
        return ans

    def get_sym(self, item_id: ItemId):
        item = self.get_item(item_id)
        if not is_sym(item):
            raise invalid_item_type_error(item, "sym")
        return cast(Sym, item)

    def get_syms(self, sym_ids: List[ItemId]):
        ans: List[Sym] = []
        for id in sym_ids:
            sym = self.get_sym(id)
            ans.append(sym)
        return ans

    def get_flow(self, item_id: ItemId):
        item = self.get_item(item_id)
        if not is_flow(item):
            raise invalid_item_type_error(item, "flow")
        return as_flow(item)

    def get_flows(self, flow_ids: List[ItemId]):
        ans: List[Flow] = []
        for id in flow_ids:
            flow = self.get_flow(id)
            ans.append(flow)
        return ans

    def variable(self, name: str, formula: Formula):
        raw_name = name
        pure_name = self.pure_variable_name(name)
        if pure_name in self.variables.keys():
            return self.assign_variable(raw_name, formula)
        else:
            # self.variables[name] = self.identifier(name)
            return self.define_variable(raw_name, formula)

    def pure_variable_name(self, name: str):
        idx = re.split(pattern=r"\[(.*?)\]+", string=name)
        name = idx[0]
        return name

    def indent_up(self):
        self.indent += 1

    def indent_down(self):
        self.indent -= 1

    def item(self, item: Item):
        t = item["itemType"]
        if is_sym(item):
            sym = cast(Sym, item)
            if t == "terminal-start":
                text = get_option_value_as_str(sym, "テキスト")
                return self.terminal_start_sym(
                    sym,
                    text,
                )
            elif t == "terminal-end":
                hasReturnValue = get_option_value_as_bool(sym, "戻り値を返す")
                returnValue = get_option_value_as_formula(sym, "戻り値")
                return self.terminal_end_sym(
                    sym,
                    hasReturnValue,
                    returnValue,
                )
            elif t == "calc":
                # option
                # option mube be
                formula = get_option_value_as_formula(sym, "式")
                calc = get_option_value_as_str(sym, "代入先変数")
                return self.calc_sym(
                    sym,
                    formula,
                    calc,
                )
            elif t == "output":
                target = get_option_value_as_formula(sym, "表示対象")
                return self.output_sym(
                    sym,
                    target,
                )
            elif t == "input":
                variable = get_option_value_as_str(sym, "入力先変数")
                is_number = get_option_value_as_bool(sym, "数字で入力")
                return self.input_sym(
                    sym,
                    variable,
                    is_number,
                )
            elif t == "while":
                condition = get_option_value_as_formula(sym, "ループ条件")
                timing = get_option_value_as_str(sym, "判定タイミング")
                return self.while_sym(
                    sym,
                    sym["childrenItemIds"][0],
                    condition,
                    timing,
                )
            elif t == "for":
                variable = get_option_value_as_str(sym, "ループ変数")
                first = get_option_value_as_formula(sym, "初期値")
                condition = get_option_value_as_formula(sym, "条件")
                increment = get_option_value_as_formula(sym, "増分")
                return self.for_sym(
                    sym,
                    sym["childrenItemIds"][0],
                    variable,
                    first,
                    condition,
                    increment,
                )
            elif t == "if":
                condition = get_option_value_as_formula(sym, "条件")
                return self.if_sym(
                    sym,
                    sym["childrenItemIds"][0],
                    sym["childrenItemIds"][1],
                    condition
                )
            elif t == "switch":
                condition = get_option_value_as_formula(sym, "条件")
                return self.switch_sym(
                    sym,
                    sym["childrenItemIds"],
                    condition,
                )
            elif t == "prepare":
                target = get_option_value_as_str(sym, "準備対象")
                target_type = get_option_value_as_str(sym, "種類")
                first = get_option_value_as_formula(sym, "初期値")
                count = get_option_value_as_str(sym, "要素数")
                simple_disp = get_option_value_as_bool(sym, "簡易表示")
                count = count.split("*")
                count = list(map(lambda c: int(c), count))
                return self.prepare_sym(
                    sym,
                    target,
                    target_type,
                    first,
                    count,
                    simple_disp,
                )
            elif t == "process":
                process_name = get_option_value_as_str(sym, "処理名")
                return self.process_sym(
                    sym,
                    process_name,
                )
            else:
                raise NotImplementedError(f"invalid sym type : {t}")
        elif is_flow(item):
            flow = as_flow(item)
            return self.flow(flow, childIds=flow["childrenItemIds"], is_top=False, tag=flow["tag"])
        else:
            raise invalid_item_type_error(item, "sym or flow")

    Lines = List[str]

    # def list_to_line(self, lines: Lines):
    #     ans = ""
    #     for line in lines:
    #         ans += line
    #     return ans

    def get_flow_name(self, flow: Flow):
        if self.is_main_flow(flow):
            return self.get_main_flow_name()
        first_sym_id = flow["childrenItemIds"][0]
        first_sym = self.get_sym(first_sym_id)
        name = get_option_value(first_sym, "テキスト")
        return name

    def is_main_flow(self, flow: Flow):
        return flow == self.get_item(self.flowIds[0])

    def get_main_flow_name(self):
        return "main"

    def comment_line(self, content: str):
        return self.line(self.comment(content))

    def flow_lines(self, flow: Flow, is_top: bool = False):
        return self.flow(
            flow,
            flow["childrenItemIds"],
            is_top,
            flow["tag"],
        )

    def start_variable_scope(self):
        self._variable_snapshot = self.variables.copy()

    def end_variable_scope(self):
        if self._variable_snapshot is None:
            return
        self.variables = cast(Variables, self._variable_snapshot)
        self._variable_snapshot = None

    def get_title(self):
        return self.title

    # オーバーライド

    def assign_variable(self, name: str, formula: Formula):
        return self.comment(f"変数 {formula} へ {self.identifier(name)} を代入")

    def define_variable(self, name: str, formula: Formula):
        self.variables[name] = self.identifier(name)
        return self.comment(f"変数 {self.identifier(name)} を初期値 {formula} で宣言")

    def comment(self, msg: str) -> str:
        # raise NotImplementedError()
        return f"// {msg}"

    def line(self, content: str) -> str:
        return self.get_indent()+content+self.get_newline()

    def get_newline(self):
        return "\n"

    def get_indent(self):
        return self.indent_str * self.indent

    def identifier(self, in_flowchart_name: str) -> str:
        return in_flowchart_name

    def flow(self, flow: Flow, childIds: List[ItemId], is_top: bool, tag: str):
        flow = as_flow(flow)

        def children_contents():
            # builder = CodeBuilder("")
            builder = CodeBuilder("")
            # linesに行を追加
            for id in childIds:
                _item = self.get_item(id)
                builder.add(self.item(_item))
            return builder.get()

        ans = ""
        if is_top:
            # variable_snapshot = self.variables.copy()
            # 関数定義
            builder = CodeBuilder("")
            builder.add(self.line(
                f"関数 {self.get_flow_name(flow)}()"
            ))
            self.indent_up()
            builder.add(children_contents())
            self.indent_down()
            # self.variables = variable_snapshot
            ans = builder.get()
        else:
            # 行の集まり
            ans = children_contents()
        return ans

    @item_one_line
    def terminal_start_sym(self, sym: Sym, text: str):
        return self.comment("はじめ")

    @item_one_line
    def terminal_end_sym(self, sym: Sym, hasReturnValue: bool, returnValue: Formula):
        return self.comment("おわり")

    @item_one_line
    def calc_sym(self, sym: Sym, formula: Formula, variable: str):
        return self.variable(variable, formula)

    @item_one_line
    def output_sym(self, sym: Sym, target: Formula):
        return self.comment(f"出力({target})")

    @item_one_line
    def input_sym(self, sym: Sym, variable: str, is_number: bool):
        return self.comment(f"input {variable}")

    def while_sym(self, sym: Sym, childId: ItemId, condition: Formula, timing: str):
        flow = self.get_flow(childId)
        b = CodeBuilder("")
        b.add(self.line(self.comment(f"{condition} の間")))
        self.indent_up()
        b.add(self.flow(
            flow,
            flow["childrenItemIds"],
            False,
            flow["tag"]
        ))
        self.indent_down()
        b.add(self.line(self.comment("を繰り返す")))
        return b.get()

    def for_sym(self,
                sym: Sym,
                childId: ItemId,
                variable: str,
                first: Formula,
                condition: Formula,
                increment: Formula
                ):
        builder = CodeBuilder("")
        flow = self.get_flow(childId)
        builder.add(self.line(self.variable(variable, first)))
        builder.add(self.line(self.comment(f"for {condition}")))
        self.indent_up()
        builder.add(self.flow(
            flow,
            flow["childrenItemIds"],
            False,
            flow["tag"]
        ))
        self.indent_down()
        builder.add(self.line(self.variable(
            variable, f"{variable} + {increment}")))
        return builder.get()

    def if_sym(
        self,
        sym: Sym,
        yes_flow_id: ItemId,
        no_flow_id: ItemId,
        condition: Formula
    ):
        yes_flow = self.get_flow(yes_flow_id)
        no_flow = self.get_flow(no_flow_id)
        builder = CodeBuilder("")
        builder.add(self.line(self.comment(f"もし {condition} なら")))
        self.indent_up()
        builder.add(self.flow(
            yes_flow,
            yes_flow["childrenItemIds"],
            False,
            yes_flow["tag"],
        ))
        self.indent_down()
        builder.add(self.line(self.comment("そうでないなら")))
        self.indent_up()
        builder.add(self.flow(
            no_flow,
            no_flow["childrenItemIds"],
            False,
            no_flow["tag"],
        ))
        self.indent_down()
        builder.add(self.line(self.comment("を実行する")))
        return builder.get()

    def switch_sym(
        self,
        sym: Sym,
        child_ids: List[ItemId],
        condition: Formula
    ):
        builder = CodeBuilder("")
        builder.add(self.line(self.comment(f"もし {condition} が")))
        for child_id in child_ids:
            child = self.get_flow(child_id)
            tag = child["tag"]
            self.indent_up()
            builder.add(self.line(self.comment(f"{tag} なら")))
            self.indent_up()
            builder.add(
                self.flow(
                    child,
                    child["childrenItemIds"],
                    False,
                    tag,
                )
            )
            self.indent_down()
            self.indent_down()
        builder.add(self.line(self.comment(f"を実行する")))
        return builder.get()

    @item_one_line
    def prepare_sym(
        self,
        sym: Sym,
        target: str,
        target_type: str,
        first: Formula,
        count: List[int],
        simple_disp: bool
    ):
        return self.comment("準備")

    @item_one_line
    def process_sym(self, sym: Sym, process_name: str):
        return self.comment("定義済み処理")


def already_exists_variable(name: str):
    return LookupError(f"already exists variable : {name}")


def not_exists_item_error(item_id: ItemId):
    return LookupError(f"not exists item : id:{item_id}")


def multi_exists_item_error(item_id: ItemId):
    return LookupError(f"exist many items : id:{item_id}")


def invalid_item_type_error(item: Item, ideal: str):
    return TypeError(f"invalid type of {item} . must be {ideal}")


def option_as_str_error(item: Item, name: str):
    return TypeError(f"{name} option of {item} must be str")


def option_as_str(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == str):
        raise option_as_str_error(item, name)
    return op_v


def option_as_int_error(item: Item, name: str):
    return TypeError(f"{name} option of {item} must be int")


def option_as_int(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == int):
        raise option_as_int_error(item, name)
    return op_v


def option_as_bool_error(item: Item, name: str):
    return TypeError(f"{name} option of {item} must be bool")


def option_as_bool(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == bool):
        raise option_as_bool_error(item, name)
    return op_v


def option_as_formula_error(item: Item, name: str):
    return TypeError(f"{name} option of {item} must be formula")


def option_as_formula(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == Formula):
        raise option_as_formula_error(item, name)


class CodeBuilder:
    def __init__(self, init=""):
        self.str = init

    def add(self, *contents: str):
        for content in contents:
            self.str += content

    def get(self):
        return self.str

    def __str__(self) -> str:
        return self.get()


def as_flow(arg: Any) -> Flow:
    if not is_flow(arg):
        raise invalid_item_type_error(arg, "Flow")
    return cast(Flow, arg)


def as_sym(arg: Any) -> Sym:
    if not is_sym(arg):
        raise invalid_item_type_error(arg, "Sym")
    return cast(Sym, arg)


def as_item(arg: Any) -> Item:
    if not is_item(arg):
        raise invalid_item_type_error(arg, "Item")
    return cast(Item, arg)
