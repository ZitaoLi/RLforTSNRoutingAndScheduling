import unittest
from net_env import *
import numpy as np


class MyTest(unittest.TestCase):

    def setUp(self) -> None:
        edges_list = [(1, 2), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (5, 6)]
        bandwidth_list = [1] * 7  # basic unit is 1B/ns
        propagation_delay_list = [0] * 7
        process_delay_list = [0] * 7

        flows = {
            '1': Flow(multi_flow_id=1, flow_id=1, flow_size=1500, flow_cycle=100000, talker=1, listener=6,
                      paths=[(1, 2), (2, 3), (3, 5), (5, 6)], schedules=list()),
            '2': Flow(multi_flow_id=2, flow_id=2, flow_size=1500, flow_cycle=50000, talker=1, listener=6,
                      paths=[(1, 2), (2, 3), (3, 5), (5, 6)], schedules=list()),
            '3': Flow(multi_flow_id=2, flow_id=3, flow_size=1500, flow_cycle=50000, talker=1, listener=6,
                      paths=[(1, 2), (2, 3), (3, 5), (5, 6)], schedules=list()),
        }

        cycles = [100000, 50000]
        hp = int(np.lcm.reduce(cycles))
        time_slot_len = int(100 / 1)
        time_slot_num = int(np.ceil(hp / time_slot_len))

        self.params = {
            'edges_list': edges_list,
            'bandwidth_list': bandwidth_list,
            'propagation_delay_list': propagation_delay_list,
            'process_delay_list': process_delay_list,
            'flows': flows,
            'time_len': hp,  # 100us
            'time_slot_len': time_slot_len,  # 100B / 1Gbps = 100ns
            'time_slot_num': time_slot_num,  # 100us / 100ns = 1000
        }
        self.topo: Topo = Topo(**self.params)

    def test_time_slot_allocation(self):
        self.topo.allocate_time_slots(self.params['flows']['1'], [1, 2], 0, 15)

        hp = self.topo.di_graph.edges[1, 2]['hyper_period']

        # different multi-flows, closed
        assignable: bool = hp._check_assignable(self.params['flows']['2'], 9, 15, 2)
        print(assignable)

        # different multi-flows stick
        assignable: bool = hp._check_assignable(self.params['flows']['2'], 110, 15, 2)
        print(assignable)
        self.topo.allocate_time_slots(self.params['flows']['2'], [1, 2], 110, 15)

        # the same multi-flow, closed
        assignable: bool = hp._check_assignable(self.params['flows']['1'], 5, 15, 1)
        print(assignable)
        self.topo.allocate_time_slots(self.params['flows']['1'], [1, 2], 5, 15)

        # the same multi-flow, different flows, stick
        assignable: bool = hp._check_assignable(self.params['flows']['3'], 25, 15, 10)
        print(assignable)
        self.topo.allocate_time_slots(self.params['flows']['3'], [1, 2], 25, 15)

        print(self.topo)

    def test_remove_flow(self):
        self.topo.allocate_time_slots(self.params['flows']['1'], [1, 2], 0, 15)
        self.topo.allocate_time_slots(self.params['flows']['2'], [1, 2], 110, 15)
        self.topo.allocate_time_slots(self.params['flows']['1'], [1, 2], 5, 15)
        self.topo.allocate_time_slots(self.params['flows']['3'], [1, 2], 25, 15)
        print(self.topo)

        self.topo.remove_flow(self.params['flows']['1'])
        print(self.topo)

    def test_step(self):
        env = NetEnv(**self.params)
        env.step(0, 1, [1, 2])
        env.step(15, 2, [1, 2])
        env.step(15, 3, [1, 2])

        print(env.topo)


if __name__ == '__main__':
    unittest.main()
