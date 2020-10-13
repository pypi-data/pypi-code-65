__version__ = '0.1.0'
from composable.pipeable import (

    pipeable, 
    )

from composable.utility import pipeable_all_in_module
import toolz.curried.operator as operator

pipeable_all_in_module(operator)