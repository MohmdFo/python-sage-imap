import logging
from typing import List

from sage_imap.exceptions import (
    IMAPFolderExistsError,
    IMAPFolderNotFoundError,
    IMAPFolderOperationError,
    IMAPUnexpectedError,
)
from sage_imap.helpers.mailbox import DefaultMailboxes
from sage_imap.services.client import IMAPClient

logger = logging.getLogger(__name__)


class IMAPFolderService:
    """A service class for managing IMAP folders.

    Purpose
    -------
    This class provides methods to create, rename, delete, and list folders in an IMAP
    mailbox.
    It interacts with the IMAP server through an IMAPClient instance and handles
    folder-related operations
    with appropriate error handling and logging.

    Parameters
    ----------
    client : IMAPClient
        An instance of the IMAPClient class used to communicate with the IMAP server.

    Methods
    -------
    rename_folder(old_name: str, new_name: str)
        Renames an existing folder.
    delete_folder(folder_name: str)
        Deletes a specified folder.
    create_folder(folder_name: str)
        Creates a new folder.
    list_folders()
        Lists all folders in the mailbox.

    Example
    -------
    >>> client = IMAPClient('imap.example.com', 'username', 'password')
    >>> folder_service = IMAPFolderService(client)
    >>> folder_service.create_folder('NewFolder')
    >>> folder_service.rename_folder('NewFolder', 'RenamedFolder')
    >>> folder_service.delete_folder('RenamedFolder')
    >>> folders = folder_service.list_folders()
    """

    def __init__(self, client: IMAPClient):
        self.client = client

    def rename_folder(self, old_name: str, new_name: str) -> None:
        """Renames an existing folder.

        Purpose
        -------
        This method renames an existing folder from `old_name` to `new_name`.

        Parameters
        ----------
        old_name : str
            The current name of the folder to be renamed.
        new_name : str
            The new name for the folder.

        Raises
        ------
        IMAPFolderNotFoundError
            If the folder to be renamed does not exist.
        IMAPFolderOperationError
            If the folder rename operation fails.

        Example
        -------
        >>> folder_service.rename_folder('OldFolder', 'NewFolder')
        """
        try:
            logger.debug("Renaming folder from %s to %s", old_name, new_name)
            status, response = self.client.rename(  # type: ignore[attr-defined]
                old_name, new_name
            )
            response_str = response[0].decode("utf-8") if response else ""
            if status != "OK":
                if "NONEXISTENT" in response_str:
                    logger.error(
                        "Failed to rename folder from `%s` to `%s`: Folder does not "
                        "exist.",
                        old_name,
                        new_name,
                    )
                    raise IMAPFolderNotFoundError(
                        f"Failed to rename folder from `{old_name}` to `{new_name}`: "
                        "Folder does not exist."
                    )
                logger.error(
                    "Failed to rename folder from `%s` to `%s`: %s",
                    old_name,
                    new_name,
                    response_str,
                )
                raise IMAPFolderOperationError(
                    f"Failed to rename folder from {old_name} to {new_name}."
                )
            logger.info("Successfully renamed folder from %s to %s", old_name, new_name)
        except Exception as e:
            logger.error(
                "Exception occurred while renaming folder from %s to %s: %s",
                old_name,
                new_name,
                e,
            )
            raise IMAPFolderOperationError(
                f"Failed to rename folder from {old_name} to {new_name}."
            ) from e

    def delete_folder(self, folder_name: str) -> None:
        """Deletes a specified folder.

        Purpose
        -------
        This method deletes a folder with the given `folder_name`. It cannot delete
        default folders.

        Parameters
        ----------
        folder_name : str
            The name of the folder to be deleted.

        Raises
        ------
        IMAPUnexpectedError
            If attempting to delete a default folder.
        IMAPFolderNotFoundError
            If the folder to be deleted does not exist.
        IMAPFolderOperationError
            If the folder deletion operation fails.

        Example
        -------
        >>> folder_service.delete_folder('FolderName')
        """
        if (
            folder_name
            in DefaultMailboxes._value2member_map_  # pylint: disable=protected-access
        ):
            logger.error("Cannot delete default folder: %s", folder_name)
            raise IMAPUnexpectedError(f"Cannot delete default folder: {folder_name}")
        try:
            logger.debug("Deleting folder: %s", folder_name)
            status, response = self.client.delete(  # type: ignore[attr-defined]
                folder_name
            )
            response_str = response[0].decode("utf-8") if response else ""
            if status != "OK":
                if "NONEXISTENT" in response_str:
                    logger.error(
                        "Failed to delete folder `%s`: Folder does not exist.",
                        folder_name,
                    )
                    raise IMAPFolderNotFoundError(
                        f"Failed to delete folder {folder_name}: Folder does not exist."
                    )
                logger.error(
                    "Failed to delete folder `%s`: %s", folder_name, response_str
                )
                raise IMAPFolderOperationError(
                    f"Failed to delete folder {folder_name}."
                )
            logger.info("Successfully deleted folder: %s", folder_name)
        except Exception as e:
            logger.error(
                "Exception occurred while deleting folder %s: %s", folder_name, e
            )
            raise IMAPFolderOperationError(
                f"Failed to delete folder {folder_name}."
            ) from e

    def create_folder(self, folder_name: str) -> None:
        """Creates a new folder.

        Purpose
        -------
        This method creates a new folder with the given `folder_name`.

        Parameters
        ----------
        folder_name : str
            The name of the folder to be created.

        Raises
        ------
        IMAPFolderExistsError
            If the folder already exists.
        IMAPFolderOperationError
            If the folder creation operation fails.

        Example
        -------
        >>> folder_service.create_folder('NewFolder')
        """
        try:
            logger.debug("Creating folder: `%s`", folder_name)
            status, response = self.client.create(  # type: ignore[attr-defined]
                folder_name
            )
            response_str = response[0].decode("utf-8") if response else ""
            if status != "OK":
                if "ALREADYEXISTS" in response_str:
                    logger.error(
                        "Failed to create folder `%s`: Folder already exists.",
                        folder_name,
                    )
                    raise IMAPFolderExistsError(
                        f"Failed to create folder {folder_name}: Folder already exists."
                    )
                logger.error(
                    "Failed to create folder `%s`: %s", folder_name, response_str
                )
                raise IMAPFolderOperationError(
                    f"Failed to create folder {folder_name}."
                )
            logger.info("Successfully created folder: `%s`", folder_name)
        except Exception as e:
            logger.error(
                "Exception occurred while creating folder `%s`: %s", folder_name, e
            )
            raise IMAPFolderOperationError(
                f"Failed to create folder {folder_name}."
            ) from e

    def list_folders(self) -> List[str]:
        """Lists all folders in the mailbox.

        Purpose
        -------
        This method retrieves a list of all folders in the mailbox.

        Returns
        -------
        List[str]
            A list of folder names.

        Raises
        ------
        IMAPFolderOperationError
            If the folder listing operation fails.

        Example
        -------
        >>> folders = folder_service.list_folders()
        >>> print(folders)
        ['INBOX', 'Sent', 'Drafts']
        """
        try:
            logger.debug("Listing all folders")
            status, response = self.client.list()  # type: ignore[attr-defined]
            if status != "OK":
                logger.error("Failed to list folders: %s", response)
                raise IMAPFolderOperationError("Failed to list folders.")

            folders = [folder.decode("utf-8").split(' "/" ')[1] for folder in response]
            logger.debug("Successfully listed folders: %s", folders)
            return folders
        except Exception as e:
            logger.error("Exception occurred while listing folders: %s", e)
            raise IMAPFolderOperationError("Failed to list folders.") from e