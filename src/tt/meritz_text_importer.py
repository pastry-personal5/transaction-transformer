from tt.automated_text_importer_base_impl import AutomatedTextImporterBaseImpl
from tt.simple_transaction import SimpleTransaction


class MeritzTextImporter(AutomatedTextImporterBaseImpl):

    def __init__(self):
        super().__init__()

    def concat_and_cleanup_local_files_if_needed(self) -> bool:
        # Implementation for Meritz
        pass

    def import_transactions(self, concatenated_file_meta: list[tuple[str, str]]) -> (bool, list[SimpleTransaction]):
        # Implementation for Meritz
        pass
