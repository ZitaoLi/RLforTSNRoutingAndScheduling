from net_env import *


class Flow:

    def __init__(self, **kwargs):
        self.m_fid: FlowId = kwargs['multi_flow_id']
        self.fid: FlowId = kwargs['flow_id']
        self.size: int = kwargs['flow_size']
        self.cycle: int = kwargs['flow_cycle']
        self.talker: NodeId = kwargs['talker']
        self.listener: NodeId = kwargs['listener']
        self.paths: List[Tuple[NodeId, NodeId]] = kwargs['paths']
        self.schedules: List[int] = [-1] * len(kwargs['paths'])
        self.current_hop: int = 0  # current hop, used to get time slot offset from schedules
        self.state: str = 'pending'  # failed, pending, succeed

    def get_last_hop_time_slot_offset(self):
        if self.current_hop == 0:
            return -1
        else:
            return self.schedules[self.current_hop - 1]
