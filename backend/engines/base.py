import abc

class BaseEngineAdapter(abc.ABC):
    """Base interface for all AI engines."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The identifier of the engine (e.g., 'wan2gp')."""
        pass

    @abc.abstractmethod
    async def process_job(
        self,
        job_id: str,
        voice_id: str,
        avatar_url: str,
        script_text: str
    ) -> str:
        """
        Executes the AI task.
        Should raise an Exception if the execution fails.
        Returns the resulting file URL/path.
        """
        pass
