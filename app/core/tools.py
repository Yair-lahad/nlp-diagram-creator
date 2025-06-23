"""
Core diagram generation tools.
"""

import uuid
from pathlib import Path
from typing import List
import importlib
from app.core.models import Node, Connection
from diagrams import Diagram, Cluster


class DiagramTools:
    """Diagram tools for creating and rendering diagrams"""

    NODE_MAPPINGS = {
        "ec2": ("diagrams.aws.compute", "EC2"),
        "rds": ("diagrams.aws.database", "RDS"),
        "elb": ("diagrams.aws.network", "ELB")
    }

    def __init__(self):
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)

    def create_node(self, name: str, node_type: str, cluster: str = None) -> Node:
        """Create a node - returns node object"""
        if node_type not in self.NODE_MAPPINGS:
            raise ValueError(f"Unsupported node type: {node_type}")

        return Node(name, node_type, cluster)

    def connect_nodes(self, from_node: str, to_node: str) -> Connection:
        """Create connection - returns connection object"""
        return Connection(from_node, to_node)

    def render_diagram(self, nodes: List[Node], connections: List[Connection],
                       title: str = "Infrastructure Diagram") -> str:
        """Render diagram from provided nodes and connections"""
        if not nodes:
            raise ValueError("No nodes to render")

        filename = f"diagram_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{filename}.png"

        try:
            self._render_with_diagrams(nodes, connections, title, output_path)
            return str(output_path)
        except ImportError:
            return f"[MOCK] {output_path}"

    def _render_with_diagrams(self, nodes: List[Node], connections: List[Connection],
                              title: str, output_path: Path):
        """Actual rendering logic"""
        with Diagram(title, filename=str(output_path.with_suffix("")), show=False):
            diagram_nodes = {}
            # Group by cluster
            clusters = {}
            for node in nodes:
                if node.cluster:
                    clusters.setdefault(node.cluster, []).append(node)
                else:
                    diagram_nodes[node.name] = self._create_diagram_node(node)
            # Create clustered nodes
            for cluster_name, cluster_nodes in clusters.items():
                with Cluster(cluster_name):
                    for node in cluster_nodes:
                        diagram_nodes[node.name] = self._create_diagram_node(
                            node)
            # Create connections
            for conn in connections:
                diagram_nodes[conn.from_node] >> diagram_nodes[conn.to_node]

    def _create_diagram_node(self, node: Node):
        """Create actual diagram node object"""
        module_name, class_name = self.NODE_MAPPINGS[node.node_type]
        module = importlib.import_module(module_name)
        node_class = getattr(module, class_name)
        return node_class(node.name)
