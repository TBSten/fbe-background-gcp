
from typing import List

from v2.types import Flow, ItemId, Sym, invalid_value_error
from ..Converter import CodeBuilder, Converter, Formula, item_one_line


class JavaScriptConverter(Converter):
    def __init__(self, fbe):
        super().__init__(fbe)

    def convert(self) -> str:
        builder = CodeBuilder()
        builder.add(super().convert())
        builder.add(self.line("main()"))
        return builder.get()

    def flow(
        self,
        flow: Flow,
        childIds: List[ItemId],
        is_top: bool,
        tag: str,
    ):
        self.start_variable_scope()
        builder = CodeBuilder()
        if is_top:
            name = self.get_flow_name(flow)
            builder.add(self.line(f"function {name} ()"+"{"))
            self.indent_up()
        for id in childIds:
            child = self.get_item(id)
            builder.add(self.item(child))
        if is_top:
            self.indent_down()
            builder.add(self.line("}"))
        ans = builder.get()
        self.end_variable_scope()
        return ans

    def assign_variable(self, name: str, formula: Formula):
        super().assign_variable(name, formula)
        return f"{name} = {formula}"

    def define_variable(self, name: str, formula: Formula):
        super().define_variable(name, formula)
        return f"let {name} = {formula}"

    @item_one_line
    def input_sym(self, sym: Sym, variable: str, is_number: bool):
        if is_number:
            return self.variable(variable, f"parseFloat(prompt())")
        else:
            return self.variable(variable, f"prompt()")

    @item_one_line
    def output_sym(self, sym: Sym, target: Formula):
        return f"alert({target})"

    def if_sym(
        self,
        sym: Sym,
        yes_flow_id: ItemId,
        no_flow_id: ItemId,
        condition: Formula
    ):
        yes_flow = self.get_flow(yes_flow_id)
        no_flow = self.get_flow(no_flow_id)
        builder = CodeBuilder()
        builder.add(self.line(f"if({condition})"+"{"))
        self.indent_up()
        builder.add(
            self.flow(
                yes_flow, yes_flow["childrenItemIds"],
                False,
                yes_flow["tag"]
            )
        )
        self.indent_down()
        builder.add(self.line("}else{"))
        self.indent_up()
        builder.add(
            self.flow(
                no_flow, no_flow["childrenItemIds"],
                False,
                no_flow["tag"]
            )
        )
        self.indent_down()
        builder.add(self.line("}"))
        return builder.get()

    def while_sym(
        self,
        sym: Sym,
        childId: ItemId,
        condition: Formula,
        timing: str
    ):
        child = self.get_flow(childId)
        builder = CodeBuilder()
        if timing == "前判定":
            builder.add(self.line(f"while({condition})"+"{"))
            self.indent_up()
            builder.add(self.flow(
                child,
                child["childrenItemIds"],
                False,
                child["tag"],
            ))
            self.indent_down()
            builder.add(self.line("}"))
        elif timing == "後判定":
            builder.add(self.line(f"do "+"{"))
            builder.add(self.flow(
                child,
                child["childrenItemIds"],
                False,
                child["tag"],
            ))
            builder.add(self.line("}"+f" while({condition})"))
        else:
            raise invalid_value_error(timing, "'前判定' or '後判定'")
        return builder.get()

    def for_sym(
        self,
        sym: Sym,
        childId: ItemId,
        variable: str,
        first: Formula,
        condition: Formula,
        increment: Formula
    ):
        child = self.get_flow(childId)
        builder = CodeBuilder()
        builder.add(self.line(
            f"for(let {variable} = {first} ; {condition} ; {variable} += {increment})"+"{"
        ))
        self.indent_up()
        builder.add(
            self.flow(
                child,
                child["childrenItemIds"],
                False,
                child["tag"],
            )
        )
        self.indent_down()
        builder.add(self.line("}"))
        return builder.get()

    def switch_sym(self, sym: Sym, child_ids: List[ItemId], condition: Formula):
        builder = CodeBuilder()
        builder.add(self.line(f"switch({condition})"+"{"))
        self.indent_up()
        for id in child_ids:
            child = self.get_flow(id)
            tag = child["tag"]
            if tag == "その他":
                builder.add(self.line(f"default"))
            else:
                builder.add(self.line(f"case {child['tag']} :"))
            self.indent_up()
            builder.add(self.flow(
                child,
                child["childrenItemIds"],
                False,
                child["tag"],
            ))
            builder.add(self.line(f"break;"))
            self.indent_down()
        self.indent_down()
        builder.add(self.line("}"))
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
        formula = ""
        if target_type == "1次元配列":
            formula = f"Array({count[0]}).fill({first})"
        elif target_type == "2次元配列":
            formula = f"Array({count[0]}).fill(Array({count[1]}).fill({first}))"
        else:
            raise invalid_value_error("", "'1次元配列' or '2次元配列'")
        return self.variable(
            target,
            formula,
        )

    def process_sym(self, sym: Sym, process_name: str):
        builder = CodeBuilder()
        builder.add(self.comment_line(
            f"「{process_name}」の呼び出し"
        ))
        builder.add(self.line(
            f"{process_name}()"
        ))
        return builder.get()

    def terminal_start_sym(self, sym: Sym, text: str):
        return ""

    def terminal_end_sym(self, sym: Sym, hasReturnValue: bool, returnValue: Formula):
        return ""
