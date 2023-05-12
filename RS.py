"""
Implementation of network simulation using the RPL protocol
"""

import simpy
import math
import random

msgCount = 0

class Network:
    """
    Network class
    """
    def __init__(self, env):
        self.env = env
        self.nodes = []

    def add_node(self, node_id, position):
        new_node = Node(self.env, node_id, position)
        self.nodes.append(new_node)
        return new_node

    def get_node(self, node_id):
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None



class DIO_Message:
    """
    DIO (DODAG Information Object) messages class:
    - Used for network discovery and configuration. 
    - Sent periodically or in response to a DIS message 
    """
    def __init__(self, sender, rank):
        self.sender = sender
        self.rank = rank


class DIS_Message:
    """
    DIS (DODAG Information Solicitation) messages class:
    - Solicit DIO messages from its neighbors
    - Used when a new node in the network wants to join the DODAG
    """
    def __init__(self, sender):
        self.sender = sender


class DAO_Message:
    """
    DAO (Destination Advertisement Object) messages class:
    - Propagates destination information upwards in the DODAG towards the root 
    - Helps to build the routing table and establish routes from the root to the leaves
    """
    def __init__(self, sender, prefix):
        self.sender = sender
        self.prefix = prefix


class Node:
    
    """
    Node class
    """
    def __init__(self, env, node_id, position):
        self.env = env
        self.node_id = node_id
        self.position = position
        self.neighbors = []
        self.rank = float('inf')  # Initially set to infinity
        self.parent = None
        self.dio_count = 0
        self.address = f"aaaa::{node_id}"
        self.children = []


    def add_neighbor(self, neighbor_node):
        """
        Adding neighbor node to the list of neighbors
        """
        if neighbor_node not in self.neighbors:
            self.neighbors.append(neighbor_node)

    def remove_neighbor(self, neighbor_node):
        if neighbor_node in self.neighbors:
            self.neighbors.remove(neighbor_node)

    def distance(self, other_node):
        dx = self.position[0] - other_node.position[0]
        dy = self.position[1] - other_node.position[1]
        return math.sqrt(dx**2 + dy**2)

    def discover_neighbors(self, network, max_distance):
        for node in network.nodes:
            if node != self and self.distance(node) <= max_distance:
                self.add_neighbor(node)

    def send_dio(self):
        global msgCount
        for neighbor in self.neighbors:
            rank = self.rank + self.distance(neighbor)
            dio_msg = DIO_Message(self, rank)
            neighbor.process_dio(dio_msg)
            msgCount += 1

    def process_dio(self, dio_msg):
        if dio_msg.rank < self.rank:
            self.rank = dio_msg.rank
            self.parent = dio_msg.sender
            self.send_dio()
        self.dio_count += 1

    def send_dis(self):
        global msgCount
        dis_msg = DIS_Message(self)
        for neighbor in self.neighbors:
            neighbor.process_dis(dis_msg)
            msgCount += 1

    def process_dis(self, dis_msg):
        self.send_dio_to(dis_msg.sender)

    def send_dio_to(self, target_node):
        global msgCount
        rank = self.rank + self.distance(target_node)
        dio_msg = DIO_Message(self, rank)
        target_node.process_dio(dio_msg)
        msgCount += 1

    def send_dao(self):
        global msgCount
        if self.parent:
            dao_msg = DAO_Message(self, self.address)
            self.parent.process_dao(dao_msg)
            msgCount += 1

    def process_dao(self, dao_msg):
        if not ((dao_msg.sender.node_id, dao_msg.prefix) in self.children):
            self.children.append((dao_msg.sender.node_id, dao_msg.prefix))
        if self.parent:
            self.send_dao()  # Forward DAO message up the DODAG
    
    def repair(self):
        self.rank += 10  # Increase rank to initiate local repair
        self.send_dio()  # Broadcast updated DIO message

    def trickle(self, I_min, I_max, k):
        I = I_min
        t = I / 2 + random.uniform(0, I / 2)

        while I <= I_max:
            yield self.env.timeout(t)
            if self.dio_count < k:
                self.send_dis()
            self.dio_count = 0
            I *= 2
            t = I / 2 + random.uniform(0, I / 2)

    

if __name__ == "__main__":
    """
    Test cases
    """    
    #create environment and network
    env = simpy.Environment()
    network = Network(env)

    #Test case 1
    node1 = network.add_node(1, (0, 0))
    node2 = network.add_node(2, (1, 0))
    node3 = network.add_node(3, (0, 1))
    node4 = network.add_node(4, (1, 1))
    node5 = network.add_node(5, (1, 2))
    node6 = network.add_node(6, (2, 1))
    node8 = network.add_node(8, (0, 2))

    # neighbor discovery Test 
    print()
    print("Test for neighbor discovery")
    discovery_radius = 1

    for node in network.nodes:
        node.discover_neighbors(network, discovery_radius)

    for node in network.nodes:
        print(f"Node {node.node_id} neighbors: {[n.node_id for n in node.neighbors]}")
        
    #DIO message test to the DODAG formation
    print()
    print("Test DIO")
    msgCount = 0
    node1.rank = 0  # Set root node
    node1.send_dio()

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")
    print(msgCount)

    #Dis test
    print()
    print("Test dis")
    msgCount = 0

    node7 = network.add_node(7, (3, 1))
    for node in network.nodes:
        node.discover_neighbors(network, discovery_radius)

    node7.send_dis()  # Node 3 sends a DIS message to its neighbors

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")
    print(msgCount)

    print()
    print("Test Trickle algorithm and addresing")
    msgCount = 0

    I_min = 1  # Minimum interval for Trickle algorithm
    I_max = 8  # Maximum interval for Trickle algorithm
    k = 1  # Redundancy constant

    #start the Trickle algorithm for each node
    for node in network.nodes:
        env.process(node.trickle(I_min, I_max, k))

    # Run the simulation for a fixed duration
    sim_duration = 20
    env.run(until=sim_duration)

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")
        print(f"Node {node.node_id} address: {node.address}")
    print(msgCount)

    #test dao
    print()
    print("Test Dao")
    msgCount = 0

    for node in network.nodes:
        if node.rank > 0:
            node.send_dao()

    for node in network.nodes:
        print(f"Node {node.node_id} children and prefixes: {node.children}")
    print(msgCount)

    #test Repair
    print()
    print("Test Repair")
    msgCount = 0

    # Simulate a problem at Node 2
    node2.repair()

    # Run the simulation for a fixed duration
    sim_duration = 40
    env.run(until=sim_duration)

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")

    print(msgCount)