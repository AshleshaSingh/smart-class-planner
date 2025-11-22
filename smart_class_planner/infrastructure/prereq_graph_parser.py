"""
This module defines the PrereqGraphParser class, which converts prerequisite data
into a graph structure representation. The graph is used by the Smart Class Planner
application to model dependencies between courses and detect circular prerequisites.

Dependencies:
    - networkx

Architecture Layer:
    Infrastructure Layer → feeds Prerequisite DAG (D4) to Repository.
"""

import networkx as nx
from typing import Dict, List, Any
from .abstract_parser import AbstractParser


class PrereqGraphParser(AbstractParser):
    """Parses prerequisite data into a directed graph structure.

    This parser is responsible for creating node–edge mappings that represent
    course dependencies. Each node corresponds to a course, and each directed
    edge indicates a prerequisite relationship.
    """

    def parse(self, source: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Builds DAG from prereq dict (e.g., from PrerequisiteScraper).

        Args:
            source: Dict[str, List[str]] of course -> prereq courses.

        Returns:
            Dict with 'graph' (networkx DiGraph), 'nodes' (list), 'edges' (list).
        
            Raises:
            ValueError: If input data is not a dictionary or has invalid structure.
        """
        if not isinstance(source, dict):
            raise ValueError("Invalid prerequisite data: expected dictionary input.")

        G = nx.DiGraph()

        # Add nodes and edges
        for course, prereqs in source.items():
            G.add_node(course)
            for prereq in prereqs:
                G.add_node(prereq)
                G.add_edge(prereq, course)  # Edge: prereq -> course

        # Check for cycles (should be DAG)
        if not nx.is_directed_acyclic_graph(G):
            print("Warning: Cycle detected in prerequisites!")
            return {}

        nodes = list(G.nodes())
        edges = list(G.edges())

        print(f"Built DAG with {len(nodes)} nodes and {len(edges)} edges.")
        return {
            "graph": G,  # NetworkX DiGraph for topological sort, etc.
            "nodes": nodes,
            "edges": edges
        }