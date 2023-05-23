"""
Implementation of network simulation using the RPL protocol
"""
import simpy
import math
import random
import matplotlib.pyplot as plt
import imageio
import os
import numpy as np

msgCount = 0
makeGIF = True

#-----------------NETWORK---------------------#
class Network:
    """
    Network class
    """
    def __init__(self, env):
        self.env = env
        self.nodes = []     #list of nodes in the network
        self.images = []

    #add node to the network 
    def add_node(self, node_id, position):
        node = Node(self.env, self, node_id, position)#information: node id and position 
        self.nodes.append(node)
        self.visualize(f'Added node {node_id}')
        return node

    #get node from the network
    def get_node(self, node_id):
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    
    def visualize(self, title):
        global makeGIF
        if makeGIF:
            plt.figure(figsize=(6,6))
            plt.xlim(-1, 5)
            plt.ylim(-1, 5)
            for node in self.nodes:
                color = 'g' if node.rank == 0 else 'r' if node.rank > 50 else 'b'
                plt.scatter(*node.position, c=color)
                if node.parent:
                    plt.plot(*zip(node.position, node.parent.position), 'k-')
            plt.title(title)
            filename = f'output_{len(self.images)}.png'
            plt.savefig(filename)
            self.images.append(imageio.imread(filename))
            plt.close()

#-----------------CONTROL MESSAGES---------------------#
class DIO_Message:
    """
    DIO (DODAG Information Object) messages class:
    - Used for network discovery and configuration. 
    - Sent periodically or in response to a DIS message 
    - Shares information about the DODAG
    """
    def __init__(self, sender, rank):
        self.sender = sender
        self.rank = rank


class DIS_Message:
    """
    DIS (DODAG Information Solicitation) messages class:
    - Solicit DIO messages from its neighbors
    - Used when a new node in the network wants to join the DODAG
    - Requests information about the DODAG
    """
    def __init__(self, sender):
        self.sender = sender


class DAO_Message:
    """
    DAO (Destination Advertisement Object) messages class:
    - Propagates destination information upwards in the DODAG towards the root 
    - Helps to build the routing table and establish routes from the root to the leaves
    - 
    """
    def __init__(self, sender, prefix):
        self.sender = sender
        self.prefix = prefix


#-----------------NODE---------------------#
class Node:
    """
    Node class
    """
    def __init__(self, env, network, node_id, position):
        self.env = env
        self.network = network
        self.node_id = node_id
        self.position = position
        self.neighbors = []
        self.rank = float('inf')  # Initially set to infinity
        self.parent = None
        self.dio_count = 0
        self.address = f"aaaa::{node_id}"
        self.children = []

    """
    Functions 
    """
    #add neighbor to the list of neighbors
    def add_neighbor(self, neighbor_node):
        if neighbor_node not in self.neighbors:
            self.neighbors.append(neighbor_node)

    #remove neighbor from the list of neighbors
    def remove_neighbor(self, neighbor_node):
        if neighbor_node in self.neighbors:
            self.neighbors.remove(neighbor_node)

    #calculate distance between two nodes based on distance formula
    def distance(self, other_node):
        dx = self.position[0] - other_node.position[0]
        dy = self.position[1] - other_node.position[1]
        return math.sqrt(dx**2 + dy**2)

    #discover neighbouring nodes in the network. Nodes are added if they are within a certain distance
    def discover_neighbors(self, network, max_distance):
        for node in network.nodes:
            if node != self and self.distance(node) <= max_distance:
                self.add_neighbor(node)
        self.network.visualize(f'Node {self.node_id} discovered neighbors')


    """
    Protocol functions 
    """
    #send dio messages to all neighbors
    def send_dio(self):
        global msgCount                                 #global variable to count the number of messages sent        
       
        for neighbor in self.neighbors:                 #message content: rank is based on distances to neighbors. increases as more nodes are added to the network
            rank = self.rank + self.distance(neighbor)  
            dio_msg = DIO_Message(self, rank)
            neighbor.process_dio(dio_msg)               #all neighbors process the dio message
            msgCount += 1
        self.network.visualize(f'Node {self.node_id} sent DIO message')

    #process dio message
    def process_dio(self, dio_msg):
        if dio_msg.rank < self.rank:                    #rank rule in RPL: node's rank must be greater than its parent's rank 
            self.rank = dio_msg.rank                    
            self.parent = dio_msg.sender                #parent is the node that sent the dio message
            self.send_dio()                             #keep sending dio messages to neighbors until no candidate parents are found
        self.dio_count += 1                             #number of consistsen DIO messages received. used as counter in trickle algorithm
        self.network.visualize(f'Node {self.node_id} processed DAO message')

    #send dio message to specific node
    def send_dio_to(self, target_node):
        global msgCount                                 
        rank = self.rank + self.distance(target_node)   #update rank
        dio_msg = DIO_Message(self, rank)
        target_node.process_dio(dio_msg)                
        msgCount += 1


    #send dis message to all neighbors
    def send_dis(self):
        global msgCount
        dis_msg = DIS_Message(self)

        #going through all neighbors and sending dis message to each one
        for neighbor in self.neighbors:
            neighbor.process_dis(dis_msg)
            msgCount += 1

    #send dio messages to node that sent dis message
    def process_dis(self, dis_msg):
        self.send_dio_to(dis_msg.sender)


    #send dao messages 
    def send_dao(self):
        global msgCount
        if self.parent:                                     #only send dao message if node has a parent
            dao_msg = DAO_Message(self, self.address)       
            self.parent.process_dao(dao_msg)
            msgCount += 1
        #self.network.visualize(f'Node {self.node_id} sent DAO message')

    #process dao messages
    def process_dao(self, dao_msg):
        #add the node that has sent the dao message to the list of children of not already in the list
        if not ((dao_msg.sender.node_id, dao_msg.prefix) in self.children):
            self.children.append((dao_msg.sender.node_id, dao_msg.prefix))
        
        #forward DAO message up the DODAG
        if self.parent:
            self.send_dao()                                                    

    """
    Transmission functions
    """
    #LOOK MORE INTO THIS 
    def repair(self):
        self.rank += 10  # Increase rank to initiate local repair
        self.send_dio()  # Broadcast updated DIO message
        #self.network.visualize(f'Node {self.node_id} initiated local repair')

    #trickle algorithm
    def trickle(self, I_min, I_max, k):
        I = I_min                               #minimum interval
        t = I / 2 + random.uniform(0, I / 2)    #determine random time between I_min/2 and I_min 
        self.dio_count = 0
        #keep sending dis messages until I_max is reached: If max is reached then the least energy is used 
        while I <= I_max:
            yield self.env.timeout(t)       #wait for t time units i.e. node is idle/listening 
            if self.dio_count < k:          #node decides whether to transmit its own control message i.e DIS message if its counter is less than k (user-defined threshold)
                self.send_dis()
            
            #if no DIS messages are received within time interval, the interval is doubled for the next round in order to reduce the number of transmissions
            self.dio_count = 0
            I *= 2
            t = I / 2 + random.uniform(0, I / 2)


#-----------------TEST CASES---------------------#
if __name__ == "__main__":

    #create environment and network
    env = simpy.Environment()
    network = Network(env)

    
    """
    Test case 1: 8 node network 
    """
    node1 = network.add_node(1, (0, 0))
    node2 = network.add_node(2, (1, 0))
    node3 = network.add_node(3, (0, 1))
    node4 = network.add_node(4, (1, 1))
    node5 = network.add_node(5, (1, 2))
    node6 = network.add_node(6, (2, 1))
    node8 = network.add_node(8, (0, 2))

    #----------------------Test: Neighbor discovery----------------------
    print("\nTest for neighbor discovery")
    
    discovery_radius = 1
    for node in network.nodes:
        node.discover_neighbors(network, discovery_radius)

    for node in network.nodes:
        print(f"Node {node.node_id} neighbors: {[n.node_id for n in node.neighbors]}")
        

    #----------------------Test: DIO message test to form DODAG----------------------
    print("\nTest DIO")
    msgCount = 0
    node1.rank = 0             #set root node
    node1.send_dio()           #send DIO message to all neighbors from root 

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")
    
    print("Number of messages: ", msgCount)


    #Test: Add new node into network and send DIS messages
    print("\nTest dis")
    msgCount = 0
    node7 = network.add_node(7, (3, 1))  

    for node in network.nodes:
        node.discover_neighbors(network, discovery_radius)  #node 7 discovers neighbours 

    node7.send_dis()                                        #node 7 sends a DIS message to its neighbors

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")
    print("Number of messages: ", msgCount)

    #----------------------Test: Trickle algorithm and addresing----------------------
    makeGIF = False
    print("\nTest Trickle algorithm and addresing")
    msgCount = 0

    I_min = 1  # Minimum interval for Trickle algorithm
    I_max = 8  # Maximum interval for Trickle algorithm
    k = 1      # Redundancy constant

    for node in network.nodes:
        env.process(node.trickle(I_min, I_max, k))   #start the Trickle algorithm for each node

    sim_duration = 20                                #run the simulation for 20 time units
    env.run(until=sim_duration)

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")
        print(f"Node {node.node_id} address: {node.address}")
    print("Number of messages: ", msgCount)

    #----------------------Test: DAO messages----------------------
    print("\nTest Dao")
    msgCount = 0

    for node in network.nodes:
        if node.rank > 0:
            node.send_dao()

    for node in network.nodes:
        print(f"Node {node.node_id} children and prefixes: {node.children}")
    print("Number of messages: ", msgCount)

    #----------------------Test: Repair----------------------
    print("\nTest Repair")
    msgCount = 0

    node2.repair()                  #simulate a problem at Node 2
    sim_duration = 40               #run the simulation for 40 time units
    env.run(until=sim_duration)

    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}")
        print(f"Node {node.node_id} parent: {node.parent.node_id if node.parent else None}")

    print("Number of messages: ", msgCount)


    """
    Considerations:
    - Remove node from network? 
    - More extensive control messages and rank calculation 
    - Network development 
    - More extensive testing
    - "Lossy" nodes
    - "Lossy" links
    - "Lossy" messages
    - More "real world" simulation
    """
    # Create the GIF
    imageio.mimsave('output.gif', network.images, loop = 1)

    # Remove the individual images after creating the GIF
    for i in range(len(network.images)):
        os.remove(f'output_{i}.png')
