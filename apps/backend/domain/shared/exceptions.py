class BaseAppException(Exception):
    """Base exception for all application-specific errors."""
    pass


class LLMProviderError(BaseAppException):
    """Raised when an LLM provider fails to generate a response."""
    pass


class LLMProviderTimeoutError(LLMProviderError):
    """Raised when the LLM provider request times out."""
    pass


class LLMValidationError(LLMProviderError):
    """Raised when the LLM response fails validation against the requested schema."""
    pass
