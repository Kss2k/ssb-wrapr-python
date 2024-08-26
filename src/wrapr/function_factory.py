import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
import pandas as pd
import numpy as np

from rpy2.robjects import pandas2ri, numpy2ri
from rpy2.robjects.help import HelpNotFoundError
from typing import Any, Callable, List, Set, Tuple

from .convert import convertR2py
from .renv import Renv
from .load_namespace import try_load_namespace
from .utils import pinfo


def base_func(func: Callable | Any, renv: Renv): # should be a Callable, but may f-up
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


def attach_to_namespace(namespace: Renv, name: str, attr: Any) -> None:
    # return: funcs, other-assets
    if attr is None: 
        return
    setattr(namespace, name, attr)


def func_factory(env_name: str,
                 module: None | rpkg.Package = None,
                 namespace: None | Renv = None,
                 select = "*") -> Renv:
    if module is None or namespace is None:
        pinfo("Loading packages...", verbose=True)
        module = try_load_namespace(env_name, verbose=True)
        namespace = Renv()
    funcs, datasets = get_assets(env_name, module=module, select=select)

    pinfo("Indexing assests in library, this might take a while...",
          verbose=True)
    for f in funcs:
        attach_to_namespace(namespace, name=f, 
                            attr=base_func(getattr(module, f), 
                                           renv=namespace))

    for d in datasets: 
        attach_to_namespace(namespace, name=d, attr=fetch_data(d, module))

    pinfo("Done!", verbose=True)
    return namespace


def attach_base(renv: Renv) -> None:
    for pkg in renv.Renvironments:
        func_factory(env_name = pkg,
                     module = renv.Renvironments[pkg],
                     namespace = renv)
    
        
def get_assets(env_name: str, module: rpkg.Package, 
               select: List[str] | Tuple[str]) -> Tuple[Set[str], Set[str]]:
    rcode: str = f"library({env_name}); ls(\"package:{env_name}\")"
    # rcode: str = f"ls(\"package:{env_name}\")"
    rattrs: Set[str] = set(ro.r(rcode, invisible=True, print_r_warnings=False))
    pyattrs: Set[str] = set(dir(module))
    
    # return: funcs, other-assets
    functions = rattrs & pyattrs
    other_assets = rattrs - pyattrs

    # filter
    if select != "all" or select != "*":
        functions = functions & set(select)
        other_assets = other_assets & set(select)

    return (functions, other_assets)
