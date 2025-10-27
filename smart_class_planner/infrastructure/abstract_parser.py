"""
Description:
    Defines a common interface for all parsers and web scrapers
    used in the Smart Class Planning Tool. This supports a
    plug-and-play infrastructure layer where each parser can
    be replaced or extended independently.

Architecture Layer:
    Infrastructure Layer → feeds parsed data into Domain Repository.
"""

from abc import ABC, abstractmethod
from typing import Any


class AbstractParser(ABC):
    """Abstract base class for all parser and crawler modules."""

    @abstractmethod
    def parse(self, source: Any) -> Any:
        """
        Abstract parse method to be implemented by subclasses.

        Args:
            source: The input file path, URL, or raw text data.

        Returns:
            Parsed structured data object (dict, list, or domain model).
        """
        pass