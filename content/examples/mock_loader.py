import sys
from types import ModuleType
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec

class DynamicMock(ModuleType):
    __path__ = []
    __all__ = []

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        child = DynamicMock(f"{self.__name__}.{name}")
        setattr(self, name, child)
        sys.modules[f"{self.__name__}.{name}"] = child
        return child

    def __call__(self, *args, **kwargs):
        return DynamicMock(f"{self.__name__}()")

class SelectiveMockFinder(MetaPathFinder, Loader):
    def __init__(self, mock_targets):
        self.mock_targets = mock_targets

    def find_spec(self, fullname, path, target=None):
        if any(fullname == t or fullname.startswith(t + ".") for t in self.mock_targets):
            return ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        if spec.name in sys.modules:
            return sys.modules[spec.name]
        return DynamicMock(spec.name)

    def exec_module(self, module):
        pass

import micropip
async def install_packages():
    await micropip.install(["unitaria", "tequila-basic", "sympy", "scipy", "jax", "autograd", "rich"], deps=False)

    sys.meta_path.append(SelectiveMockFinder(["openfermion"]))

