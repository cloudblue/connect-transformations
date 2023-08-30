import itertools

from connect_transformations.formula.functions.common import functions as common_functions
from connect_transformations.formula.functions.pricing import functions as pricing_functions


all_functions = ''.join(itertools.chain(common_functions, pricing_functions))
all_functions = all_functions.replace('    ', '').replace('\n', '')
