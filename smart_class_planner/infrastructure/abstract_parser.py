"""
File: abstract_parser.py
------------------------

This module defines core infrastructure components for the Smart Class Planner system.
It includes various parsers, data loaders, and scrapers responsible for extracting and 
preparing academic planning data from PDFs, Excel sheets, and web sources.

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