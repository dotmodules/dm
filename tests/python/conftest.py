# NOTE: Since pytest-pdd is based on decorated function and the decorated
# function names are generated dynamically, we don't know the step definition's
# name at import time. Hence the star import..
# More details on this:
# https://github.com/pytest-dev/pytest-bdd/blob/master/src/pytest_bdd/steps.py#L176

from .step_definitions import *
