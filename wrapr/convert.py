import pandas as pd
import numpy as np
import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
import rpy2.rlike.container as rcnt

from copy import Error
from rpy2.robjects import DataFrame, pandas2ri, numpy2ri
from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, OrderedDict, Set, Tuple

from .nputils import np_collapse
from .rutils import as_matrix, get_rclass
from .renv import Renv


def convertR2py(x: Any, renv: Renv) -> Any:
    match x:
        case ro.methods.RS4():
            return convert_s4(x, renv=renv)
        case vc.DataFrame():
            return convert_pandas(x)
        case vc.Vector():
            return convert_numpy(x)
        case list():
            return convert_list(x, renv=renv)
        case tuple(): 
            return convert_list(x, renv=renv)
        case rcnt.OrdDict():
            return convert_dict(dict(x), renv=renv)
        case dict():
            return convert_dict(x, renv=renv)
        case pd.DataFrame():
            return x
        case np.ndarray():
            if not is_valid_numpy(x):
                return attempt_pandas_conversion(x)
        case _:
            return generic_conversion(x)
        

def convert_list(X: List | Tuple, renv: Renv) -> Any:
    try:
        out = pd.DataFrame(X)
    except Error:
        out = [convertR2py(x, renv=renv) for x in X]
        if isinstance(X, tuple):
            out = tuple(out)
    return out
        
                
def convert_dict(X: Dict | OrderedDict, renv: Renv) -> Any:
    for key in X:
        X[key] = convertR2py(X[key], renv=renv)
    return X


def convert_numpy(x: vc.Vector | NDArray) -> NDArray:
    match x:
        case vc.BoolVector():
            dtype = "bool"
        case _:
            dtype = None
    out = np.asarray(x, dtype=dtype)
    if not out.shape:
        return out[np.newaxis][0]
    return out


def is_valid_numpy(x: NDArray) -> bool:
    return x.dtype.fields is None


def convert_pandas(df: vc.DataFrame) -> pd.DataFrame:
    with (ro.default_converter + pandas2ri.converter).context():
        pd_df = ro.conversion.get_conversion().rpy2py(df)
    return pd_df


def attempt_pandas_conversion(x: Any) -> Any:
    try: 
        return pd.DataFrame(x)
    except:
        return x


def generic_conversion(x: Any) -> Any:
    try:
        arr = np.asarray(x)
        if not is_valid_numpy(arr):
            raise Error
        return arr
    except: 
        return attempt_pandas_conversion(x)


def convert_s4(x: ro.methods.RS4, renv: Renv) -> Any:
    rclass = get_rclass(x, renv=renv)
    if rclass is None:
        return generic_conversion(x)

    match np_collapse(rclass):
        case "dgCMatrix":
            return convert_numpy(as_matrix(x, renv=renv))
        case _:
            return generic_conversion(x)

