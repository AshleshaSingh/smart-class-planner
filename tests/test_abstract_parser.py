"""
Unit tests for abstract_parser.py
"""

import pytest
from smart_class_planner.infrastructure.abstract_parser import AbstractParser

class DummyParser(AbstractParser):
    def parse(self, path):
        return f"Parsed: {path}"

def test_parse_abstract_method():
    parser = DummyParser()
    result = parser.parse("dummy.txt")
    assert result == "Parsed: dummy.txt"

def test_unimplemented_parser_raises():
    class IncompleteParser(AbstractParser):
        pass

    with pytest.raises(TypeError):
        IncompleteParser()
