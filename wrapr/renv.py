import rpy2.robjects as ro

from typing import Tuple
from wrapr.load_namespace import load_base_envs


class Renv:
    def __init__(self):
        self.Renvironments = load_base_envs()
        return None
    



