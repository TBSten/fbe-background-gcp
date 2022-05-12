from typing import Dict, List, Union, cast
from v2.Converter import CodeBuilder, Converter, Variables, item_one_line
from v2.formula_resolver import Type, Types, resolve_type
from v2.types import FBEFormat, Flow, Formula, ItemId, Sym, invalid_value_error


JAVA_TEMPLATE = """
~~~~~ imports ~~~~~
class Main {
    ~~~~~ imports ~~~~~
    ~~~~~ methods ~~~~~
}
""".strip()

CODES = {
    "STRING_INPUT": "sc.next()",
    "INT_INPUT": "sc.nextInt()",
    "DOUBLE_INPUT": "sc.nextDouble()",
}


class JavaConverter(Converter):
    def __init__(self, fbe: FBEFormat) -> None:
        super().__init__(fbe)
        self.variable_types: Dict[str, Type] = {}
        self.imports: List[str] = []
        self.fields: List[str] = [
            "static Main main = new Main();"
        ]

    def convert(self) -> str:
        top = self.line("class Main {")
        self.indent_up()
        methods = super().convert()
        fields = self._fields_to_code()
        self.indent_down()
        bottom = self.line("} // Main")
        imports = self._imports_to_code()

        builder = CodeBuilder()

        builder.add(imports)
        builder.add(top)
        builder.add(fields)
        builder.add(methods)
        builder.add(bottom)
        return builder.get()

    def _imports_to_code(self):
        builder = CodeBuilder()
        for line in self.imports:
            builder.add(self.line(line))
        builder.add(self.line(""))
        return builder.get()

    def _fields_to_code(self):
        builder = CodeBuilder()
        for line in self.fields:
            builder.add(self.line(line))
        return builder.get()

    def define_variable(
        self,
        name: str,
        formula: Formula,
        t: Union[Type, None] = None,
    ):
        super().define_variable(name, formula)
        if t is None:
            t = resolve_type(formula, self.variable_types)
        t = cast(Type, t)
        self.variable_types[name] = t
        java_t = self.to_java_type(t, formula)
        return f"{java_t} {self.identifier(name)} = {formula} ;"

    def assign_variable(self, name: str, formula: Formula):
        return f"{self.identifier(name)} = {formula} ;"

    def to_java_type(self, t: Type, formula: Formula = ""):
        if formula == CODES["STRING_INPUT"]:
            return "String"
        if formula == CODES["INT_INPUT"]:
            return "int"
        if formula == CODES["DOUBLE_INPUT"]:
            return "double"

        if t == Types.BOOLEAN:
            return "boolean"
        elif t == Types.DOUBLE:
            return "double"
        elif t == Types.INTEGER:
            return "int"
        elif t == Types.STRING:
            return "String"
        elif Types.is_array(t):
            return f"{self.to_java_type(t.dep)}[]"
        elif t == Types.UNKNOWN:
            return "Object"
        else:
            raise invalid_value_error(t, "TYPE")

    def global_variable(self, name: str, formula: Formula):
        self.variable(name, formula)

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
            if self.is_main_flow(flow):
                builder.add(
                    self.line(f"public static void main (String[] args)"+"{"))
            else:
                builder.add(self.line(f"void {name} ()"+"{"))
            self.indent_up()
        for id in childIds:
            child = self.get_item(id)
            builder.add(self.item(child))
        if is_top:
            name = self.get_flow_name(flow)
            self.indent_down()
            builder.add(self.line("} "+f"// {name}"))
            builder.add(self.line(""))
        ans = builder.get()
        self.end_variable_scope()
        return ans

    def terminal_start_sym(self, sym: Sym, text: str):
        return ""

    def terminal_end_sym(self, sym: Sym, hasReturnValue: bool, returnValue: Formula):
        return ""

    @item_one_line
    def output_sym(self, sym: Sym, target: Formula):
        return f"System.out.println({target});"

    @item_one_line
    def input_sym(self, sym: Sym, variable: str, is_number: bool):
        w = self.indent_str
        self.indent_str = "=>"
        self.imports.append("import java.util.Scanner ;")
        self.fields.append("static Scanner sc = new Scanner();")
        self.indent_str = w
        formula = CODES["STRING_INPUT"]
        if is_number:
            formula = CODES["INT_INPUT"]
        return self.variable(variable, formula)

    def while_sym(self, sym: Sym, childId: ItemId, condition: Formula, timing: str):
        builder = CodeBuilder()

        if timing == "前判定":
            builder.add(self.line(f"while({condition})"+"{"))
            self.indent_up()
            builder.add(
                self.flow_lines(self.get_flow(childId))
            )
            self.indent_down()
            builder.add(self.line("} // while"))
        elif timing == "後判定":
            builder.add(self.line("do{"))
            self.indent_up()
            builder.add(
                self.flow_lines(self.get_flow(childId))
            )
            self.indent_down()
            builder.add(self.line("}"+f" while({condition});"))
        return builder.get()

    def if_sym(self, sym: Sym, yes_flow_id: ItemId, no_flow_id: ItemId, condition: Formula):
        builder = CodeBuilder()
        yes_flow = self.get_flow(yes_flow_id)
        no_flow = self.get_flow(no_flow_id)
        builder.add(self.line(f"if ({condition})"+"{"))
        self.indent_up()
        builder.add(self.flow_lines(yes_flow))
        self.indent_down()
        builder.add(self.line("}else{"))
        self.indent_up()
        builder.add(self.flow_lines(no_flow))
        self.indent_down()
        builder.add(self.line("}"))
        return builder.get()

    def for_sym(self, sym: Sym, childId: ItemId, variable: str, first: Formula, condition: Formula, increment: Formula):
        flow = self.get_flow(childId)
        builder = CodeBuilder()
        builder.add(self.line(
            f"for({self.variable(variable,first)} {condition} ; {variable} += {increment})"+"{"))
        self.indent_up()
        builder.add(self.flow_lines(flow))
        self.indent_down()
        builder.add(self.line("}"))
        return builder.get()

    def switch_sym(self, sym: Sym, child_ids: List[ItemId], condition: Formula):
        builder = CodeBuilder()
        builder.add(self.line(f"switch({condition})"+"{"))
        self.indent_up()
        for id in child_ids:
            flow = self.get_flow(id)
            tag = flow['tag']
            if tag == "その他":
                builder.add(self.line(f"default :"))
            else:
                builder.add(self.line(f"case {tag}:"))
            self.indent_up()
            builder.add(self.flow_lines(flow))
            builder.add(self.line(f"break;"))
            self.indent_down()
        self.indent_down()
        builder.add(self.line("}"))
        return builder.get()

    def prepare_sym(
        self,
        sym: Sym,
        target: str,
        target_type: str,
        first: Formula,
        count: List[int],
        simple_disp: bool
    ):
        type = resolve_type(first, self.variable_types)
        java_type = self.to_java_type(type)
        builder = CodeBuilder()
        builder.add(self.comment_line(
            f"{target_type} {target} を {' * '.join(map(str,count))} , 初期値 {first} で初期化"))
        if target_type == "1次元配列":
            import_statement = "import java.util.Arrays ;"
            if not (import_statement in self.imports):
                self.imports.append(import_statement)
            define_line = self.define_variable(
                target,
                f"new {java_type}[{count[0]}]",
                Types.ARRAY(type),
            )
            init_line = f"Arrays.fill({target},{first});"
            builder.add(self.line(define_line))
            builder.add(self.line(init_line))
        elif target_type == "2次元配列":
            import_statement = "import java.util.Arrays ;"
            if not (import_statement in self.imports):
                self.imports.append(import_statement)
            define_line = self.define_variable(
                target,
                f"new {java_type}[{count[0]}][{count[1]}]",
                Types.ARRAY(Types.ARRAY(type))
            )
            row = []
            for colIdx in range(0, count[1]):
                row.append(first)
            init_line = "Arrays.fill(-arr-,new -type-[]{ -row- });" \
                .replace("-arr-", target) \
                .replace("-type-", java_type) \
                .replace("-row-", f"{' , '.join(row)}")
            builder.add(self.line(define_line))
            builder.add(self.line(init_line))
        else:
            raise invalid_value_error("", "'1次元配列' or '2次元配列'")
        builder.add(self.line(""))
        return builder.get()

    @ item_one_line
    def process_sym(self, sym: Sym, process_name: str):
        return f"main.{self.identifier(process_name)}();"
