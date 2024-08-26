import numpy as np

from numpy.typing import NDArray
from rpy2.rlike.container import Any
from typing import Callable

from .renv import Renv


def get_rclass(x: Any, renv: Renv) -> NDArray[np.unicode_] | None:
    try:
        f: Callable = getattr(renv.Renvironments["base"], "class")
        return np.asarray(f(x), dtype = "U")
    except:
        return None


def as_matrix(x: Any, renv: Renv) -> NDArray | Any:
    return renv.Renvironments["Matrix"].as_matrix(x)
