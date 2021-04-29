from net_env import *
import math


class NetEnv:

    def __init__(self, **kwargs):
        self.hyper_period_len: int = kwargs['time_len']  # length of hyper period
        self.time_slot_len: int = kwargs['time_slot_len']  # length of time slot
        self.time_slot_num: int = kwargs['time_slot_num']  # number of time slots
        self.edges_list: List[List[NodeId, NodeId]] = kwargs['edges_list']
        self.bandwidth_list: List[int] = kwargs['bandwidth_list']

        self.flows: Dict[str, Flow] = kwargs['flows']

        self._build_net()

    def _build_net(self):
        self.topo: Topo = Topo(edges_list=self.edges_list,
                               bandwidth_list=self.bandwidth_list,
                               time_len=self.hyper_period_len,
                               time_slot_len=self.time_slot_len,
                               time_slot_num=self.time_slot_num)

    def step(self, action: int, current_flow_id: FlowId, current_edge: List):
        flow: Flow = self.flows[str(current_flow_id)]
        edge = self.topo.get_edge(current_edge[0], current_edge[1])
        allocated_len: int = math.ceil(flow.size / edge['bandwidth'] / self.time_slot_len)
        self.topo.allocate_time_slots(flow, current_edge, action, allocated_len)

    def reset(self):
        pass
