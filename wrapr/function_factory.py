import rpy2
import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
import pandas as pd
import numpy as np

from rpy2.robjects import pandas2ri, numpy2ri
from rpy2.robjects.help import HelpNotFoundError, Package
from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, Set, Tuple

from .convert import convert_numpy, convertR2py
from .renv import Renv
from .load_namespace import try_load_namespace


def base_func(func: Callable | Any, renv: Renv): # should be a Callable, but may f-up
    if not callable(func):
        return None

    def wrap(*args, **kwargs):
        with (ro.default_converter + pandas2ri.converter + 
              numpy2ri.converter).context():
            result: Any = convertR2py(func(*args, **kwargs), renv=renv)
        return result

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


def attach_to_namespace(namespace: Renv, name: str, attr: Any) -> None:
    if attr is None: 
        return
    setattr(namespace, name, attr)


def func_factory(env_name: str,
                 module: None | rpkg.Package = None,
                 namespace: None | Renv = None) -> Renv:
    if module is None or namespace is None:
        module = try_load_namespace(env_name)
        namespace = Renv()
    funcs, datasets = get_assets(env_name, module=module)

    for f in funcs:
        attach_to_namespace(namespace, name=f, 
                            attr=base_func(getattr(module, f), 
                                           renv=namespace))

    for d in datasets: 
        attach_to_namespace(namespace, name=d, attr=fetch_data(d, module))

    return namespace


def attach_base(renv: Renv) -> None:
    for pkg in renv.Renvironments:
        func_factory(env_name = pkg,
                     module = renv.Renvironments[pkg],
                     namespace = renv)
    
        
def get_assets(env_name: str, module: rpkg.Package) -> Tuple[Set[str], Set[str]]:
    rcode: str = f"library({env_name}); ls(\"package:{env_name}\")"
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: Set[str] = set(ro.r(rcode, invisible=True, print_r_warnings=False))
    pyattrs: Set[str] = set(dir(module))
    # return: funcs, other-assets
    return (rattrs & pyattrs, rattrs - pyattrs)
