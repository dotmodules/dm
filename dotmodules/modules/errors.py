from abc import ABC, abstractmethod
from typing import List

from dotmodules.modules.path import PathManager


class ErrorListProvider(ABC):
    @abstractmethod
    def report_errors(self, path_manager: PathManager) -> List[str]:
        """
        Method that should report the errors occured with the given object.
        """
