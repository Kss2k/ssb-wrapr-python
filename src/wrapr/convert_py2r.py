import scipy
import rpy2.robjects as ro

from types import NoneType
from collections import OrderedDict
from typing import Any, Callable, Dict, List
from rpy2.robjects import pandas2ri, numpy2ri

from .rutils import rcall


# functions for converting from py 2 R -----------------------------------------
def convert_py2R(x: Any) -> Any:
    match x:
        case scipy.sparse.coo_array() | scipy.sparse.coo_matrix():
            y = convert_pysparsematrix(x)
        case OrderedDict() | dict():
            y = dict2rlist(x)
        case NoneType():
            y = ro.NULL
        case _:
            y = x
    return y


def dict2rlist(x: Dict | OrderedDict) -> ro.ListVector:
    # clean values first
    for k, v in x.items():
        x[k] = convert_py2R(v)

    with (ro.default_converter + pandas2ri.converter + 
          numpy2ri.converter).context():
        y = ro.ListVector(x)
    return y


def convert_pysparsematrix(x: scipy.sparse.coo_array | scipy.sparse.coo_matrix):
    try:
        sparseMatrix: Callable = rcall("Matrix::sparseMatrix")
        y: Any = sparseMatrix(i=ro.IntVector(x.row + 1),
                              j=ro.IntVector(x.col + 1),
                              x=ro.FloatVector(x.data),
                              dims=ro.IntVector(x.shape))
    except:
        return x

    return y


def clean_args(args: List[Any], kwargs: Dict[str, Any]) -> None:
    for i, x in enumerate(args):
        args[i] = convert_py2R(x)
    for k, v in kwargs.items():
        kwargs[k] = convert_py2R(v)
