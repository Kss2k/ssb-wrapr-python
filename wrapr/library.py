from .function_factory import func_factory
from .renv import Renv


def library(env_name: str) -> Renv:
    return func_factory(env_name)
