from typing import Dict, List
from typing import OrderedDict as OrderedDictType

from dotmodules.modules.hooks import Hook, VariableStatusHook

AggregatedVariablesType = Dict[str, List[str]]
AggregatedHooksType = OrderedDictType[str, List[Hook]]
AggregatedVariableStatusHooksType = Dict[str, VariableStatusHook]
