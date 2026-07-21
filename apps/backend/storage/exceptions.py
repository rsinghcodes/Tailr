class StorageError(Exception):
    """Base exception for storage errors."""

    pass


class FileNotFoundStorageError(StorageError):
    """Raised when file is not found in storage."""

    pass


class InvalidPathError(StorageError):
    """Raised when path traversal or unsafe filename is detected."""

    pass


class CompilationError(Exception):
    """Raised when LaTeX compilation fails."""

    def __init__(self, message: str, log_output: str | None = None):
        super().__init__(message)
        self.message = message
        self.log_output = log_output or ""
