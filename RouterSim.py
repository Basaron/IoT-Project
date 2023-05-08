
"""
Implementation of router simulation using the RPL protocol
"""

import simpy
import random
import math

#node class
class Node:
    def __init__(self, env, node_id, x, y, network):
        self.env = env                                                              #simpy environment
        self.node_id = node_id                   
        self.x = x                                                                  #x coordinate                 
        self.y = y                                                                  #y coordinate
        self.network = network
        self.neighbors = []
        self.parent = None
        self.rank = float('inf')
        self.prefix = None
        self.routing_table = {}
        self.discovery_process = env.process(self.discover_neighbors())             #process for discovering neighbors
        self.dio_process = env.process(self.send_dio())                             #process for sending DIO messages
        self.dao_process = env.process(self.send_dao())                             #process for sending DAO messages


    def distance(self, other_node):
        """
        Calculates the distance between two nodes
        """
        return math.sqrt((self.x - other_node.x) ** 2 + (self.y - other_node.y) ** 2) #calculation is based on the distance formula


    def discover_neighbors(self):
        """
        Discovers neighbors within the network radius
        """
        while True:
            #randomly wait between 1 and 3 time units
            yield self.env.timeout(random.uniform(1, 3)) #yield is like return but for generators i.e. functions that can be paused and resumed

            #finds neighbors within the network radius
            for node in self.network.nodes:
                #checking if node is not self, distance is less than 10 and node is not already in neighbors list
                
                if node != self and node.distance(self) <= 10:
                    if node not in self.neighbors:

                        #add node to neighbors list
                        self.neighbors.append(node)

    def send_dio(self):
        """
        Sends DIO messages to neighbors
        """
        while True:

            yield self.env.timeout(random.uniform(5, 10))
            for neighbor in self.neighbors:
                neighbor.receive_dio(self)

    #receives DIO messages
    def receive_dio(self, sender):
        new_rank = sender.rank + 1
        if new_rank < self.rank:
            self.rank = new_rank
            self.parent = sender

    def send_dis(self):
        while True:
            yield self.env.timeout(random.uniform(5, 10))
            for neighbor in self.neighbors:
                neighbor.receive_dis(self)

    def receive_dis(self, sender):
        self.send_dio()

    def send_dao(self):
        while True:
            yield self.env.timeout(random.uniform(15, 20))
            if self.parent:
                self.parent.receive_dao(self)

    def receive_dao(self, sender):
        self.routing_table[sender.node_id] = sender
        if self.parent and self.parent != sender:
            self.parent.receive_dao(sender)

class Network:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        self.nodes.remove(node)

# Simulation environment setup
env = simpy.Environment()
network = Network()

# Adding nodes to the network
for i in range(10):
    x, y = random.uniform(0, 50), random.uniform(0, 50)
    node = Node(env, i, x, y, network)
    network.add_node(node)

# Designate the root node
root = random.choice(network.nodes)
root.rank = 0
root.prefix = '2001:db8::/64'

# Running the simulation for 200 time units
env.run(until=200)

# Printing the discovered neighbors, parent, and routing table for each node
for node in network.nodes:
    print(f'Node {node.node_id}: Neighbors {[n.node_id for n in node.neighbors]}, Parent {node.parent.node_id if node.parent else None}, Routing table {[n.node_id for n in node.routing_table.values()]}')



"""
----------Considerations----------
Network setup:
- Number of nodes
- Radius
- 

Netowrk efficiency:
- Throughput
- Latency
- Packet loss
- Retransmission 
- Data rate 
- Repair mechanism 
- 

Energy consumption:
- Energy consumption of each node, message and process

Other:
- Buffer overflow 
- Occupancy
- Congestion
- Priority packets
- 


Simulation/Test cases:
- Cooja? 
- Presentation content? 
- Dato for fremlæggelse? 
"""