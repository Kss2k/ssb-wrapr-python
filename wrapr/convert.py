import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro
import rpy2.robjects.vectors as vc
from rpy2.robjects import DataFrame, pandas2ri, numpy2ri

import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import Any, Callable, Dict, List, OrderedDict, Set, Tuple


def convert_container(X: Dict | OrderedDict | List | Tuple) -> Any:
    for x in X:
        match type(x):
            case vc.DataFrame:
                return pandas2ri.ri
                


def convert_numpy(x: vc.Vector) -> NDArray:
    match type(x):
        case vc.BoolVector:
            dtype = "bool"
        case _:
            dtype = None
    return np.asarray(x, dtype=dtype)



