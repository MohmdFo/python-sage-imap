from _typeshed import Incomplete
from sage_imap.exceptions import IMAPFolderExistsError as IMAPFolderExistsError, IMAPFolderNotFoundError as IMAPFolderNotFoundError, IMAPFolderOperationError as IMAPFolderOperationError, IMAPUnexpectedError as IMAPUnexpectedError
from sage_imap.helpers.mailbox import DefaultMailboxes as DefaultMailboxes
from sage_imap.services.client import IMAPClient as IMAPClient

logger: Incomplete

class IMAPFolderService:
    client: Incomplete
    def __init__(self, client: IMAPClient) -> None: ...
    def rename_folder(self, old_name: str, new_name: str) -> None: ...
    def delete_folder(self, folder_name: str) -> None: ...
    def create_folder(self, folder_name: str) -> None: ...
    def list_folders(self) -> list[str]: ...