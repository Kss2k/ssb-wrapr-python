import rpy2
from rpy2 import robjects
import rpy2.robjects.packages as rpkg


def try_load_namespace(namespace: str):
    try: 
        module: rpkg.Package = rpkg.importr(namespace)
    except rpkg.PackageNotInstalledError: 
        choice = input(namespace + " not installed, do you want to install it? (y/n)\n")
        if choice[0] != "y": 
            raise rpkg.PackageNotInstalledError
        robjects.r(f"install.packages(\"{namespace}\")")
        module: rpkg.Package = rpkg.importr(namespace)

    return module
