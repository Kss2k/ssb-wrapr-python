import wrapr as wr
from rpy2.robjects.packages import data
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import pdb
gs = wr.try_load_namespace("GaussSuppression")
modsem = wr.try_load_namespace("modsem")

ms = wr.func_factory("modsem")
m1 = """
    X =~ x1 + x2 + x3
    Y =~ y1 + y2 + y3
    Z =~ z1 + z2 + z3
    Y ~ X + Z + X:Z
"""

est = ms.modsem(m1, ms.oneInt, method = "qml")
getattr(ms, "summary_modsem_qml")(est)
