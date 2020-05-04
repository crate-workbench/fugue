import copy
from typing import Any, Callable, Dict, List, Optional, no_type_check

from fugue.creator.creator import Creator
from fugue.dataframe import DataFrame
from fugue.exceptions import FugueInterfacelessError
from fugue.utils.interfaceless import FunctionWrapper
from triad.collections import Schema
from triad.utils.assertion import assert_or_throw
from triad.utils.convert import to_function, to_instance


def creator(schema: Any = None) -> Callable[[Any], "_FuncAsCreator"]:
    # TODO: validation of schema if without * should be done at compile time
    def deco(func: Callable) -> _FuncAsCreator:
        return _FuncAsCreator.from_func(func, schema)

    return deco


def to_creator(obj: Any, schema: Any = None) -> Creator:
    exp: Optional[Exception] = None
    try:
        return copy.copy(to_instance(obj, Creator))
    except Exception as e:
        exp = e
    try:
        f = to_function(obj)
        # this is for string expression of function with decorator
        if isinstance(f, Creator):
            return copy.copy(f)
        # this is for functions without decorator
        return _FuncAsCreator.from_func(f, schema)
    except Exception as e:
        exp = e
    raise FugueInterfacelessError(f"{obj} is not a valid creator", exp)


class _FuncAsCreator(Creator):
    @no_type_check
    def create(self) -> DataFrame:
        args: List[Any] = []
        kwargs: Dict[str, Any] = {}
        if self._need_engine:  # type: ignore
            args.append(self.execution_engine)
        kwargs.update(self.params)
        return self._wrapper.run(  # type: ignore
            args=args,
            kwargs=kwargs,
            output_schema=self.output_schema if self._need_output_schema else None,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._wrapper(*args, **kwargs)  # type: ignore

    @no_type_check
    @staticmethod
    def from_func(func: Callable, schema: Any) -> "_FuncAsCreator":
        tr = _FuncAsCreator()
        tr._wrapper = FunctionWrapper(func, "^e?x*$", "^[dlsp]$")  # type: ignore
        tr._need_engine = tr._wrapper.input_code.startswith("e")
        tr._need_output_schema = "s" == tr._wrapper.output_code
        tr._output_schema = Schema(schema)
        if len(tr._output_schema) == 0:
            assert_or_throw(
                not tr._need_output_schema,
                FugueInterfacelessError(
                    f"schema must be provided for return type {tr._wrapper._rt}"
                ),
            )
        else:
            assert_or_throw(
                tr._need_output_schema,
                FugueInterfacelessError(
                    f"schema must not be provided for return type {tr._wrapper._rt}"
                ),
            )
        return tr
