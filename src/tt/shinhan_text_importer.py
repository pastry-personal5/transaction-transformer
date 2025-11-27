from tt.automated_text_importer_base_impl import AutomatedTextImporterBaseImpl
from tt.simple_transaction import SimpleTransaction

class ShinhanTextImporter(AutomatedTextImporterBaseImpl):

    def __init__(self):
        super().__init__()

    def concat_and_cleanup_local_files_if_needed(self) -> bool:
        # Implementation for Shinhan
        pass

    def import_transactions(self, concatenated_file_meta: list[tuple[str, str]]) -> (bool, list[SimpleTransaction]):
        # Implementation for Shinhan
        pass
