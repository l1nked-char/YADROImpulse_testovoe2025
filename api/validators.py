from pydantic import BaseModel, Field, field_validator
from typing import List


class Node(BaseModel):
    name: str = Field(..., min_length=1)


class Edge(BaseModel):
    source: str = Field(...)
    target: str = Field(...)


class GraphData(BaseModel):
    nodes: List[Node] = Field(..., min_length=1)
    edges: List[Edge] = Field(default_factory=list)

    @field_validator("nodes", mode='before')
    @classmethod
    def validate_nodes(cls, nodes: List[Node]) -> List[Node]:
        names = [node["name"] for node in nodes]
        if len(names) != len(set(names)):
            raise ValueError("Имена узлов должны быть уникальными")
        return nodes

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, edges: List[Edge], values) -> List[Edge]:
        node_names = {node.name for node in values.data.get("nodes", [])}
        for edge in edges:
            if edge.source not in node_names:
                raise ValueError(f"Узел '{edge.source}' не существует")
            if edge.target not in node_names:
                raise ValueError(f"Узел '{edge.target}' не существует")
        return edges
