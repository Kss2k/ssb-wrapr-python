import rpy2
import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, numpy2ri
from rpy2.robjects.help import HelpNotFoundError

import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, Set, Tuple

from wrapr.convert_numpy import convert_numpy

from .renv import Renv
from .load_namespace import try_load_namespace


def base_func(func: Callable | Any): # should be a Callable, but may f-up
    if not callable(func):
        return None

    def wrap(*args, **kwargs):
        with (ro.default_converter + pandas2ri.converter + 
              numpy2ri.converter).context():
            result: Any = func(*args, **kwargs)
        if isinstance(result, ro.vectors.Vector):
            result = convert_numpy(result)
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


def attach_to_namespace(namespace: Renv, name: str, attr: Any) -> None:
    if attr is None: 
        return
    setattr(namespace, name, attr)


def func_factory(env_name: str) -> Renv:
    module: rpkg.Package = try_load_namespace(env_name)
    namespace: Renv = Renv()
    funcs, datasets = get_assets(env_name, module=module)

    for f in funcs:
        attach_to_namespace(namespace, name=f, 
                            attr=base_func(getattr(module, f)))

    for d in datasets: 
        attach_to_namespace(namespace, name=d, attr=fetch_data(d, module))

    return namespace

        
def get_assets(env_name: str, module: rpkg.Package) -> Tuple[Set[str], Set[str]]:
    rcode: str = f"library({env_name}); ls(\"package:{env_name}\")"
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: Set[str] = set(ro.r(rcode, invisible=True, print_r_warnings=False))
    pyattrs: Set[str] = set(dir(module))
    # return: funcs, other-assets
    return (rattrs & pyattrs, rattrs - pyattrs)
