from net_env import *


class Node:

    def __init__(self, node_id: FlowId):
        self.node_id: FlowId = node_id  # node id
        self.peer_num: int = 0  # number of peers
        self.ports: List = list()
        self.adj_nodes: Dict[PortId, NodeId]
        self.adj_edges: Dict[PortId, EdgeId] = dict()
