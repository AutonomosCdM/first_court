from typing import List, Dict, Optional
from datetime import datetime
from ..models.canvas import CanvasNode, CanvasEdge, CanvasLayout

class MockCanvasService:
    def __init__(self):
        self.nodes: Dict[str, Dict[str, CanvasNode]] = {}  # case_id -> {node_id -> node}
        self.edges: Dict[str, Dict[str, CanvasEdge]] = {}  # case_id -> {edge_id -> edge}
        self.layouts: Dict[str, CanvasLayout] = {}  # case_id -> layout

    async def get_nodes(self, case_id: str) -> List[CanvasNode]:
        """Obtiene todos los nodos del canvas para un caso"""
        return list(self.nodes.get(case_id, {}).values())

    async def get_edges(self, case_id: str) -> List[CanvasEdge]:
        """Obtiene todas las conexiones entre nodos"""
        return list(self.edges.get(case_id, {}).values())

    async def get_layout(self, case_id: str) -> Optional[CanvasLayout]:
        """Obtiene la disposición del canvas"""
        return self.layouts.get(case_id)

    async def create_node(self, case_id: str, node: CanvasNode) -> CanvasNode:
        """Crea un nuevo nodo en el canvas"""
        if case_id not in self.nodes:
            self.nodes[case_id] = {}
        self.nodes[case_id][node.id] = node
        return node

    async def create_edge(self, case_id: str, edge: CanvasEdge) -> CanvasEdge:
        """Crea una nueva conexión entre nodos"""
        if case_id not in self.edges:
            self.edges[case_id] = {}
        self.edges[case_id][edge.id] = edge
        return edge

    async def update_layout(self, case_id: str, layout: CanvasLayout) -> CanvasLayout:
        """Actualiza la disposición del canvas"""
        self.layouts[case_id] = layout
        return layout

    async def get_full_state(self, case_id: str) -> Dict:
        """Obtiene el estado completo del canvas"""
        return {
            "nodes": await self.get_nodes(case_id),
            "edges": await self.get_edges(case_id),
            "layout": await self.get_layout(case_id)
        }

    async def delete_node(self, case_id: str, node_id: str) -> None:
        """Elimina un nodo y sus conexiones"""
        if case_id in self.nodes:
            self.nodes[case_id].pop(node_id, None)
            # Eliminar conexiones relacionadas
            if case_id in self.edges:
                self.edges[case_id] = {
                    edge_id: edge 
                    for edge_id, edge in self.edges[case_id].items()
                    if edge.source_id != node_id and edge.target_id != node_id
                }

    async def delete_edge(self, case_id: str, edge_id: str) -> None:
        """Elimina una conexión entre nodos"""
        if case_id in self.edges:
            self.edges[case_id].pop(edge_id, None)
