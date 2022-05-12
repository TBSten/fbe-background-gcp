from typing import List
from util import not_implement
from v2.Converter import CodeBuilder, Converter, item_one_line
from v2.types import Flow, Formula, ItemId, Sym, invalid_value_error


class PythonConverter(Converter):
    def convert(self) -> str:
        builder = CodeBuilder()
        builder.add(super().convert())
        builder.add(self.line("main()"))
        return builder.get()

    def assign_variable(self, name: str, formula: Formula):
        super().assign_variable(name, formula)
        return f"{name} = {formula}"

    def define_variable(self, name: str, formula: Formula):
        super().define_variable(name, formula)
        return f"{name} = {formula}"

    def comment(self, msg: str) -> str:
        return f"# {msg}"

    def flow(self, flow: Flow, childIds: List[ItemId], is_top: bool, tag: str):
        self.start_variable_scope()
        builder = CodeBuilder()
        if is_top:
            name = self.get_flow_name(flow)
            builder.add(self.line(f"def {name}():"))
            self.indent_up()
            builder.add(self.flow(flow, childIds, False, tag))
            self.indent_down()
            builder.add(self.line(""))
        else:
            lines = super().flow(flow, childIds, False, tag)
            if lines == "":
                builder.add(self.comment_line("何もしない"))
                builder.add(self.line("pass"))
            else:
                builder.add(lines)
        self.end_variable_scope()
        return builder.get()

    @item_one_line
    def output_sym(self, sym: Sym, target: Formula):
        return f"print( {target} )"

    @item_one_line
    def input_sym(self, sym: Sym, variable: str, is_number: bool):
        formula = f"input()"
        if is_number:
            formula = f"float( {formula} )"
        return self.variable(variable, formula)

    def while_sym(self, sym: Sym, childId: ItemId, condition: Formula, timing: str):
        child = self.get_flow(childId)
        builder = CodeBuilder()
        if timing == "前判定":
            builder.add(self.line(f"while {condition}:"))
            self.indent_up()
            builder.add(self.flow_lines(
                child,
                False,
            ))
            self.indent_down()
        elif timing == "後判定":
            builder.add(self.line(f"while True:"))
            self.indent_up()
            builder.add(self.flow_lines(
                child,
                False,
            ))
            builder.add(self.line(f"if not ({condition}) :"))
            self.indent_up()
            builder.add(self.line("break"))
            self.indent_down()
            self.indent_down()
        else:
            raise invalid_value_error(timing, "'前判定' or '後判定'")
        return builder.get()

    def if_sym(self, sym: Sym, yes_flow_id: ItemId, no_flow_id: ItemId, condition: Formula):
        yes_flow = self.get_flow(yes_flow_id)
        no_flow = self.get_flow(no_flow_id)
        builder = CodeBuilder()
        builder.add(self.line(f"if {condition}:"))
        self.indent_up()
        builder.add(self.flow_lines(yes_flow, False))
        self.indent_down()
        builder.add(self.line(f"else:"))
        self.indent_up()
        builder.add(self.flow_lines(no_flow, False))
        self.indent_down()
        return builder.get()

    def for_sym(
        self,
        sym: Sym,
        childId: ItemId,
        variable: str,
        first: Formula,
        condition: Formula,
        increment: Formula,
    ):
        child = self.get_flow(childId)
        builder = CodeBuilder()
        builder.add(self.comment_line(f"for はじめ"))
        builder.add(self.comment_line(
            f"{variable} を {first}から{increment}ずつ増やして{condition} の間"
        ))
        builder.add(self.line(self.variable(variable, first)))
        builder.add(self.line(f"while({condition}):"))
        self.indent_up()
        builder.add(self.flow_lines(child, False))
        builder.add(self.line(f"{variable} += {increment}"))
        self.indent_down()
        builder.add(self.comment_line(f"for おわり"))
        return builder.get()

    def switch_sym(self, sym: Sym, child_ids: List[ItemId], condition: Formula):
        children = self.get_flows(child_ids)
        builder = CodeBuilder()
        for idx, child in enumerate(children):
            builder.add(self.line(
                f"if {condition} == {child['tag']}:"
                if idx == 0 else
                f"else:"
                if idx == len(children)-1 else
                f"elif {condition} == {child['tag']}:"
            ))
            self.indent_up()
            builder.add(self.flow_lines(
                child,
                False,
            ))
            self.indent_down()
        return builder.get()

    @item_one_line
    def prepare_sym(
        self,
        sym: Sym,
        target: str,
        target_type: str,
        first: Formula,
        count: List[int],
        simple_disp: bool,
    ):
        formula = ""
        if target_type == "1次元配列" and len(count) >= 1:
            formula = f"[{first}] * {count}"
        elif target_type == "2次元配列" and len(count) >= 2:
            formula = f"[ [{first}] * {count[1]} ] * {count[0]}"
        else:
            raise invalid_value_error(
                f"type:{target_type} or count.len:{len(count)}",
                "type:(1次元配列 or 2次元配列) count.len:(vary by type)"
            )
        return self.variable(
            target,
            formula,
        )

    @item_one_line
    def process_sym(self, sym: Sym, process_name: str):
        return f"{process_name}()"

    def terminal_start_sym(self, sym: Sym, text: str):
        return ""

    def terminal_end_sym(self, sym: Sym, hasReturnValue: bool, returnValue: Formula):
        return ""
