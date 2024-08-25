import rpy2
import rpy2.robjects.packages as rpkg
import rpy2.robjects as ro

from typing import Dict, Tuple


def load_base_envs() -> Dict[str, rpkg.InstalledSTPackage| rpkg.InstalledPackage]:
    # set options for global environment
    rbase = try_load_namespace("base")
    rMatrix = try_load_namespace("Matrix")
    rutils = try_load_namespace("utils")
    return {"base": rbase, "Matrix": rMatrix, "utils": rutils}


def try_load_namespace(namespace: str):
    try: 
        module: rpkg.Package = rpkg.importr(namespace)
    except rpkg.PackageNotInstalledError: 
        choice = input(namespace + " not installed, do you want to install it? (y/n)\n")
        if choice[0] != "y": 
            raise rpkg.PackageNotInstalledError
        ro.r(f"install.packages(\"{namespace}\")")
        module: rpkg.Package = rpkg.importr(namespace)

    return module
