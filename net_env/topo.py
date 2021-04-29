from intervals import IntInterval
import networkx as nx
import numpy as np
from net_env import *


class HyperPeriod:

    def __str__(self) -> str:
        out: str = ''
        out += 'time_len: '
        out += str(self.time_len)
        out += ' '
        out += 'time_slot_len: '
        out += str(self.time_slot_len)
        out += ' '
        out += 'time_slot_num: '
        out += str(self.time_slot_num)
        out += ' '
        out += 'time_windows: '
        if len(self.time_windows) == 0:
            # out += '[0, '
            # out += str(self.time_slot_num)
            # out += ')'
            out += '{}'
        else:
            for time_window in self.time_windows:
                out += '{m_fid: '
                out += str(getattr(time_window, 'm_fid'))
                out += ', fid: '
                out += str(getattr(time_window, 'fid'))
                out += ', phs: '
                out += str(getattr(time_window, 'phs'))
                out += ', '
                out += str(time_window)
                out += '} '
        out += ' '
        return out

    __repr__ = __str__

    def __init__(self, **kwargs):
        self.time_len: int = kwargs['time_len']  # unit is ns
        self.time_slot_len: int = kwargs['time_slot_len']  # unit is ns
        self.time_slot_num: int = kwargs['time_slot_num']
        self.time_windows: List[IntInterval] = list()

    def _check_assignable(self, flow: Flow, time_slot_offset: int, allocated_len: int, phs_num: int) -> bool:
        cycle_time_slot_num: int = int(np.ceil(flow.cycle / self.time_slot_len))
        for phs in range(0, phs_num):
            offset: int = time_slot_offset + phs * cycle_time_slot_num
            interval: IntInterval = IntInterval.closed_open(offset, offset + allocated_len)
            for time_window in self.time_windows:
                try:
                    if time_window | interval:
                        if time_window.upper == interval.lower:
                            continue
                        elif time_window.lower == interval.upper:
                            continue
                        elif getattr(time_window, 'm_fid') != flow.m_fid:
                            return False
                        elif getattr(time_window, 'phs') != phs:
                            return False
                except Exception as e:
                    pass
        return True

    def get_feasible_region(self, flow: Flow,
                            send_delay: int, prop_delay: int, proc_delay: int, cycle_len: int) -> IntInterval:
        last_hop_time_slot_offset: int = flow.get_last_hop_time_slot_offset()
        if last_hop_time_slot_offset == -1:
            return IntInterval.closed_open(0, cycle_len)
        else:
            assignable_position: int = send_delay + prop_delay + proc_delay + last_hop_time_slot_offset
            return IntInterval.closed_open(assignable_position, assignable_position + cycle_len)
        pass

    def allocate_time_slots(self, flow: Flow, time_slot_offset: int, allocated_len: int, phs_num: int) -> bool:
        if not self._check_assignable(flow, time_slot_offset, allocated_len, phs_num):
            return False
        cycle_time_slot_num: int = int(np.ceil(flow.cycle / self.time_slot_len))
        for phs in range(0, phs_num):
            offset: int = time_slot_offset + phs * cycle_time_slot_num
            interval: IntInterval = IntInterval.closed_open(offset, offset + allocated_len)
            setattr(interval, 'm_fid', flow.m_fid)
            setattr(interval, 'fid', flow.fid)
            setattr(interval, 'phs', phs)
            self.time_windows.append(interval)
        self.time_windows.sort()
        return True

    def allocate_time_slots_m(self, fid: FlowId, time_slot_offset: int, allocated_len: int):
        interval: IntInterval = IntInterval.closed_open(time_slot_offset, time_slot_offset + allocated_len)
        flag: bool = False
        for time_window in self.time_windows:
            try:
                new_time_window_0: IntInterval = time_window | interval
                if getattr(time_window, 'fid') == fid:
                    i: int = self.time_windows.index(time_window)
                    setattr(new_time_window_0, 'fid', fid)
                    del self.time_windows[i]
                    self.time_windows.insert(i, new_time_window_0)
                    j: int = i + 1
                    if j < len(self.time_windows) and \
                            getattr(self.time_windows[j], 'fid') == fid and \
                            new_time_window_0.upper == self.time_windows[j].lower:
                        new_time_window_1: IntInterval = self.time_windows[j] | self.time_windows[i]
                        setattr(new_time_window_1, 'fid', fid)
                        del self.time_windows[i]
                        del self.time_windows[i]
                        self.time_windows.insert(i, new_time_window_1)
                    flag = True
                    break
            except Exception as e:
                pass
        if flag is False:
            setattr(interval, 'fid', fid)
            self.time_windows.append(interval)
        self.time_windows.sort()

    def remove_flow(self, flow: Flow):
        """
        remove flow from hyper period
        :param flow:
        :return:
        """
        old_time_windows: List[IntInterval] = self.time_windows
        self.time_windows = list(filter(lambda time_window: getattr(time_window, 'fid') != flow.fid, old_time_windows))


class Topo:

    def __str__(self) -> str:
        out: str = ''
        for n, nbrs in self.di_graph.adjacency():
            for nbr, attr in nbrs.items():
                out += '('
                out += str(n)
                out += ', '
                out += str(nbr)
                out += ') -> '
                out += str(attr)
                out += '\n'
        return out

    __repr__ = __str__

    def __init__(self, **kwargs):
        self._build_topo(**kwargs)

    def _init_hyper_period(self):
        pass

    def _build_topo(self, **kwargs):
        # create DiGraph from edges
        self.di_graph: nx.DiGraph = nx.DiGraph()
        self.di_graph.add_edges_from(kwargs['edges_list'])
        for i, e in enumerate(kwargs['edges_list']):
            hp: HyperPeriod = HyperPeriod(time_len=kwargs['time_len'],
                                          time_slot_len=kwargs['time_slot_len'],
                                          time_slot_num=kwargs['time_slot_num'])
            self.di_graph.add_edge(e[0], e[1], hyper_period=hp, bandwidth=kwargs['bandwidth_list'][i])

    def get_edge(self, n1: NodeId, n2: NodeId):
        return self.di_graph.edges[n1, n2]

    def allocate_time_slots(self, flow: Flow, edge: List, time_slot_offset: int, allocated_len: int) -> bool:
        e = self.di_graph.edges[edge[0], edge[1]]
        hp: HyperPeriod = e['hyper_period']
        phs_num: int = int(np.ceil(hp.time_len / flow.cycle))
        hp.allocate_time_slots(flow, time_slot_offset, allocated_len, phs_num)
        return True

    def remove_flow(self, flow: Flow):
        """
        remove flow from topology
        :param flow:
        :return:
        """
        for n, nbrs in self.di_graph.adjacency():
            for nbr, attr in nbrs.items():
                e = self.di_graph.edges[n, nbr]
                hp: HyperPeriod = e['hyper_period']
                hp.remove_flow(flow)
