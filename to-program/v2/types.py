from typing import Any, TypedDict

from typing import List, Optional, Type, TypedDict, Union, List, cast

from util import not_implement


ItemId = str
Formula = str


def is_formula(arg: Any):
    return type(arg) == str


class Item(TypedDict):
    itemId: ItemId
    itemType: str
    childrenItemIds: List[ItemId]
    parentItemId: Optional[ItemId]


OptionValue = Union[
    str, int, bool,
    List[str], List[int], List[bool],
    Type[None],
]


class Option(TypedDict):
    name: str
    value: OptionValue


def get_option(item: Item, name: str) -> Optional[Option]:
    if not is_sym(item):
        raise not_implement(f"{item} is not sym")

    sym: Sym = cast(Sym, item)
    matches = list(filter(lambda o: o["name"] == name, sym["options"]))
    if len(matches) <= 0:
        return None
    if len(matches) >= 2:
        raise not_implement(f"found many same name options : {name}")
    return matches[0]


# def get_option_value(item: Item, name: str, value_type: Type[T] = Any) -> T:
def get_option_value(item: Item, name: str):
    option = get_option(item, name)
    if (option is None):
        print("invalid option", "item", item,)
        print("name", name,)
        print("option", option,)
        raise not_implement(f"not exists {name} option of {item}")
    option = cast(Option, option)
    return option["value"]


def get_option_value_as_str(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == str):
        raise invalid_type_error(item, name)
    return cast(str, op_v)


def get_option_value_as_int(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == int):
        raise invalid_type_error(item, name)
    return cast(int, op_v)


def get_option_value_as_bool(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not (type(op_v) == bool):
        raise invalid_type_error(item, name)
    return cast(bool, op_v)


def get_option_value_as_formula(item: Item, name: str):
    op_v = get_option_value(item, name)
    if not is_formula(op_v):
        raise invalid_type_error(item, name)
    return cast(Formula, op_v)


def invalid_type_error(arg: Any, ideal: str):
    return TypeError(f"invalid type of {arg} . must be {ideal}")


def invalid_value_error(arg: Any, ideal: str):
    return TypeError(f"invalid value {arg} . must be {ideal}")


class Sym(Item):
    options: List[Option]


Items = List[Item]


class Flow(Item):
    tag: str


def is_item(arg) -> bool:  # ->TypeGuards[Item]
    return (
        type(arg) == dict and
        type(arg["itemId"]) == str and
        type(arg["itemType"]) == str and
        type(arg["childrenItemIds"]) == list and
        (
            type(arg["parentItemId"]) == str or
            arg["parentItemId"] is None
        )
    )


def is_sym(arg) -> bool:
    return (
        is_item(arg) and
        "options" in arg and
        type(arg["options"]) == list
    )


def is_flow(arg) -> bool:
    return (
        is_item(arg) and
        "tag" in arg and
        type(arg["tag"]) == str
    )


class Meta(TypedDict):
    title: str
    flowIds: List[ItemId]


class FBEFormat(TypedDict):
    version: str
    items: List[Item]
    meta: Meta


def is_fbe_format(arg):
    return (
        type(arg) == dict and
        type(arg["version"]) == str and
        type(arg["items"]) == list and
        type(arg["version"]) == str
    )
