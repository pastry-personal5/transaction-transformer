from abc import ABC, abstractmethod

from tt.simple_transaction import SimpleTransaction


class AutomatedTextImporterBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def concat_and_cleanup_local_files_if_needed(self) -> tuple[bool, list[tuple[str, str]] | None]:
        pass

    @abstractmethod
    def import_transactions(self, concatenated_file_meta: list[tuple[str, str]]) -> (bool, list[SimpleTransaction]):
        pass
