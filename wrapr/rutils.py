import numpy as np

from numpy.typing import NDArray
from rpy2.rlike.container import Any
from typing import Callable, Dict

from .renv import Renv


def get_rclass(x: Any, renv: Renv) -> NDArray[np.unicode_] | None:
    try:
        f: Callable = getattr(renv.Renvironments["rbase"], "class")
        return np.asarray(f(x), dtype = "U")
    except:
        return None


def as_matrix(x: Any, renv: Renv) -> NDArray | Any:
    return renv.Renvironments["rMatrix"].as_matrix(x)
