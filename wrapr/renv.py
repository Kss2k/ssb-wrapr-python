import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
import pandas as pd
import numpy as np

from rpy2.robjects import pandas2ri, numpy2ri
import rpy2.rlike.container as rcnt
from rpy2.robjects.help import HelpNotFoundError
from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, OrderedDict, Set, Tuple

from .load_namespace import load_base_envs, try_load_namespace
from .utils import ROutputCapture, pinfo
import rpy2.robjects.vectors as vc

from copy import Error
from .nputils import np_collapse


class Renv:
    def __init__(self, env_name):
        pinfo("Loading packages...", verbose=True)
        self.__Renvironments__ = load_base_envs()
        self.__set_base_lib__(try_load_namespace(env_name, verbose=True))
        
        funcs, datasets = get_assets(env_name, module=self.__base_lib__)
        self.__setRfuncs__(funcs) 
        self.__setRdatasets__(datasets) 

        pinfo("Done!", verbose=True)
        return None
  
    def __set_base_lib__(self, rpkg: rpkg.Package) -> None:
        self.__base_lib__ = rpkg

    def __setRfuncs__(self, funcs: set[str]) -> None:
        self.__Rfuncs__ = funcs
    
    def __setRdatasets__(self, datasets: set[str]) -> None:
        self.__Rdatasets__ = datasets

    def __attach__(self, name: str, attr: Any) -> None:
        if attr is None: 
            return
        setattr(self, name, attr)

    def __getattr__(self, name: str) -> Any:
        if self.__Rfuncs__ is None or self.__Rdatasets__ is None:
            raise ValueError("Renv is not correctly initialized")
        
        capture = ROutputCapture()
        capture.capture_r_output()

        if name in self.__Rfuncs__:
            fun: Callable = base_func(getattr(self.__base_lib__, name), 
                                      renv=self)
            self.__attach__(name=name, attr=fun)
            capture.reset_r_output()
            return getattr(self.__base_lib__, name)
        elif name in self.__Rdatasets__:
            self.__attach__(name=name, attr=fetch_data(name, self.__base_lib__))
            capture.reset_r_output()
            return getattr(self.__base_lib__, name)
        else:
            raise ValueError("Cannot index asset, IMPLEMENT SEARCHING IN BASE ENV")


def base_func(func: Callable | Any, renv: Renv) -> Callable | Any: # should be a Callable, but may f-up
    if not callable(func):
        return None

    def wrap(*args, **kwargs):
        with (ro.default_converter + pandas2ri.converter + 
              numpy2ri.converter).context():
            result: Any = func(*args, **kwargs)

        return convertR2py(result, renv=renv)

    try:
        wrap.__doc__ = func.__doc__
    except HelpNotFoundError: 
        pass
    return wrap


def fetch_data(dataset: str, module: rpkg.Package) -> pd.DataFrame | None:
    with (ro.default_converter + pandas2ri.converter).context():
        try:
            return rpkg.data(module).fetch(dataset)[dataset]
        except KeyError:
            return None
        except:
            return None

        
def get_assets(env_name: str, module: rpkg.Package) -> Tuple[Set[str], Set[str]]:
    rcode: str = f"library({env_name}); ls(\"package:{env_name}\")"
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: Set[str] = set(ro.r(rcode, invisible=True, print_r_warnings=False))
    pyattrs: Set[str] = set(dir(module))
    # return: funcs, other-assets
    return (rattrs & pyattrs, rattrs - pyattrs)

# utils 
def get_rclass(x: Any, renv: Renv) -> NDArray[np.unicode_] | None:
    try:
        f: Callable = getattr(renv.__Renvironments__["base"], "class")
        return np.asarray(f(x), dtype = "U")
    except:
        return None


def as_matrix(x: Any, renv: Renv) -> NDArray | Any:
    return renv.__Renvironments__["Matrix"].as_matrix(x)


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
        

def convert_list(X: List | Tuple, renv: Renv) -> Any:
    out = [convertR2py(x, renv=renv) for x in X]
    if isinstance(X, tuple):
        out = tuple(out)
    return out
        
                
def convert_dict(X: Dict | OrderedDict, renv: Renv, 
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

