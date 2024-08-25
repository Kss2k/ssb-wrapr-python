import wrapr as wr
import pandas as pd
import numpy as np

dplyr = wr.library("dplyr")

dplyr.last(x=np.array([1, 2, 3, 4]))

