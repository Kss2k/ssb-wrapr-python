import pandas as pd
import numpy as np
import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
import rpy2.rlike.container as rcnt

from copy import Error
from rpy2.robjects import pandas2ri
from numpy.typing import NDArray
from typing import Any, OrderedDict

from .nputils import np_collapse
from .rutils import as_matrix, get_rclass
from .renv import Renv


def convertR2py(x: Any, renv: Renv) -> Any:
    match x:
        case str() | int() | bool() | float():
            return x
        case ro.methods.RS4():
            return convert_s4(x, renv=renv)
        case vc.DataFrame():
            return convert_pandas(x)
        case vc.Vector() | vc.Matrix() | vc.Array():
            return convert_numpy(x)
        case list():
            return convert_list(x, renv=renv)
        case tuple(): 
            return convert_list(x, renv=renv)
        case rcnt.OrdDict():
            return convert_dict(x, renv=renv, is_RDict=True)
        case dict():
            return convert_dict(x, renv=renv)
        case pd.DataFrame():
            return x
        case np.ndarray():
            if not is_valid_numpy(x):
                return attempt_pandas_conversion(x)
            return filter_numpy(x)
        case _:
            return generic_conversion(x)
        

def convert_list(X: list | tuple, renv: Renv) -> Any:
    out = [convertR2py(x, renv=renv) for x in X]
    if isinstance(X, tuple):
        out = tuple(out)
    return out
        
                
def convert_dict(X: dict | OrderedDict, renv: Renv, 
                 is_RDict: bool = False) -> Any:
    try:
        # this needs to be improved considering named vectors
        if is_RDict and np.all(np.array(X.keys()) == None):
            Y = list(zip(*X.items()))[1]
            X = convertR2py(Y, renv=renv)
        elif is_RDict:
            X = dict(X)

        for key in X:
            X[key] = convertR2py(X[key], renv=renv)
    finally:
        return X


def convert_numpy(x: vc.Vector | NDArray) -> NDArray:
    match x: # this should be expanded upon
        case vc.BoolVector() | vc.BoolArray | vc.BoolMatrix:
            dtype = "bool"
        case vc.FloatVector() | vc.FloatArray | vc.FloatMatrix:
            dtype = "float"
        case vc.IntVector | vc.IntArray | vc.IntMatrix:
            dtype = "int"
        case _:
            dtype = None

    y = np.asarray(x, dtype=dtype)
    return filter_numpy(y)


def filter_numpy(x: NDArray) -> NDArray | int | str | float | bool:
    # sometimes a numpy array will have one element with shape (,)
    # this should be (1,)
    y = x[np.newaxis][0] if not x.shape else x
    # if shape is (1,) we should just return as int | str | float | bool
    # R doesn't have these types, only vectors/arrays, this will probably
    # give unexpected results for users who are unfamiliar with R, so
    # we return the first element instead
    y = y[0] if y.shape == (1,) else y
    return y


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

