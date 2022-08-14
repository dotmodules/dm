from typing import Dict, List
from typing import OrderedDict as OrderedDictType

from dotmodules.modules.hooks import Hook, VariableStatus, VariableStatusHook

AggregatedVariablesType = Dict[str, List[str]]
AggregatedHooksType = OrderedDictType[str, List[Hook]]
AggregatedVariableStatusHooksType = Dict[str, VariableStatusHook]
AggregatedVariableStatusesType = Dict[str, Dict[str, VariableStatus]]
