from abc import ABC, abstractmethod

from fugue.dataframe import DataFrame
from fugue.execution import ExecutionEngine
from fugue.utils.misc import get_attribute
from triad.collections import ParamDict, Schema


class Creator(ABC):
    """The interface is to generate single DataFrame from `params`.
    For reading data from file should be a type of Creator.
    Creator is task level extension, running on driver, and execution engine aware.

    :Notice:
    Before implementing this class, do you really need to implement this
    interface? Do you know the interfaceless feature of Fugue? Implementing Creator
    is commonly unnecessary. You can choose the interfaceless approach which may
    decouple your code from Fugue.
    """

    @abstractmethod
    def create(self) -> DataFrame:  # pragma: no cover
        """Create DataFrame on driver side

        :Notice:
        * It runs on driver side
        * The output dataframe is not necessarily local, for example a SparkDataFrame
        * It is engine aware, you can put platform dependent code in it (for example
        native pyspark code) but by doing so your code may not be portable. If you
        only use the functions of the general ExecutionEngine, it's still portable.

        :return: result dataframe
        """
        raise NotImplementedError

    @property
    def output_schema(self) -> Schema:
        return self._output_schema  # type: ignore

    @property
    def execution_engine(self) -> ExecutionEngine:
        return self._execution_engine  # type: ignore

    @property
    def params(self) -> ParamDict:
        return get_attribute(self, "_params", ParamDict)
