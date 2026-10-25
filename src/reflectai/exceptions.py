"""Domain exceptions exposed by ReflectAI."""

class ReflectAIError(Exception):
    """Base exception for expected application errors."""

class ConfigurationError(ReflectAIError):
    """Raised when application configuration is invalid."""

class ProviderError(ReflectAIError):
    """Raised when a model provider cannot complete a request."""

class SQLSafetyError(ReflectAIError, ValueError):
    """Raised when a query violates the read-only SQL policy."""

class QueryTimeoutError(ReflectAIError, TimeoutError):
    """Raised when a SQL query exceeds its execution time budget."""

class GenerationCancelled(ReflectAIError):
    """Raised when a model response is cancelled by the user."""
