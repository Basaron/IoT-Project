import time
import math
import random
from messages import DAO_Message, DIS_Message, DIO_Message

#-----------------NODE---------------------#
msg_dio_count = 0
msg_dao_count = 0
msg_dis_count = 0
msgCount = 0

class Node:
    """
    Node class
    """
    def __init__(self, env, network, node_id, position):
        self.env = env
        self.node_id = node_id
        self.network = network
        self.position = position
        self.neighbors = []
        self.rank = float('inf')  # Initially set to infinity
        self.parent = None
        self.dio_count = 0
        self.address = f"aaaa::{node_id}"
        self.routing_table = []
        self.children = []
        self.send_delay = 1

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
        #self.network.visualize(f'Node {self.node_id} discovered neighbors', self.node_id)



    """
    Protocol functions 
    """
    #send dio messages to all neighbors
    def send_dio(self):
        global msgCount
        yield self.env.timeout(self.send_delay)                                 #global variable to count the number of messages sent        
        print(self.node_id, self.env.now)
        for neighbor in self.neighbors:
            if neighbor != self.parent:                 #message content: rank is based on distances to neighbors. increases as more nodes are added to the network
                rank = self.rank + self.distance(neighbor)  
                dio_msg = DIO_Message(self, rank)
                self.network.visualize(f'Node {self.node_id} sent DIO message to {neighbor.node_id} at time {self.env.now}', self.node_id, neighbor.node_id, True, self.env.now)
                neighbor.process_dio(dio_msg)               #all neighbors process the dio message
                msgCount += 1

        yield self.env.timeout(self.send_delay)
        if not self.children:
            self.env.process(self.send_dao())
                              #wait for 1 second before sending another dio message
        
    #process dio message
    def process_dio(self, dio_msg):
        if dio_msg.rank < self.rank:                    #rank rule in RPL: node's rank must be greater than its parent's rank 
            self.rank = dio_msg.rank                    
            self.parent = dio_msg.sender                #parent is the node that sent the dio message
            self.network.visualize(f'Node {self.node_id} processed DIO message from {dio_msg.sender.node_id}, at time {self.env.now}', self.node_id, dio_msg.sender.node_id, False, self.env.now)  #parent is the node that sent the dio message
            #self.env.process(self.send_dao())
            self.env.process(self.send_dio())                             #keep sending dio messages to neighbors until no candidate parents are found
        self.dio_count += 1                             #number of consistsen DIO messages received. used as counter in trickle algorithm
                                

    #send dio message to specific node
    def send_dio_to(self, target_node):
        global msgCount                                 
        rank = self.rank + self.distance(target_node)   #update rank
        dio_msg = DIO_Message(self, rank)
        self.network.visualize(f'Node {self.node_id} sent DIO message to {target_node.node_id}, at time {self.env.now}', self.node_id, target_node.node_id, True, self.env.now)
        target_node.process_dio(dio_msg)                
        msgCount += 1


    #send dis message to all neighbors
    def send_dis(self):
        global msgCount
        dis_msg = DIS_Message(self)

        #going through all neighbors and sending dis message to each one
        for neighbor in self.neighbors:
            self.network.visualize(f'Node {self.node_id} sent DIS message to {neighbor.node_id}, at time {self.env.now}', self.node_id, neighbor.node_id, True, self.env.now)
            neighbor.process_dis(dis_msg)
            msgCount += 1
        
        yield self.env.timeout(self.send_delay)  # add this line to create a delay after sending dis messages


    #send dio messages to node that sent dis message
    def process_dis(self, dis_msg):
        self.send_dio_to(dis_msg.sender)

    #send dao messages 
    def send_dao(self):
        global msgCount
        if self.parent:                                     #only send dao message if node has a parent
            dao_msg = DAO_Message(self, self.address, self.routing_table)
            self.network.visualize(f'Node {self.node_id} sent DAO message to {self.parent.node_id}, at time {self.env.now}', self.node_id, self.parent.node_id, True, self.env.now)     
            self.parent.process_dao(dao_msg)
            msgCount += 1
        yield self.env.timeout(self.send_delay) 


    #process dao messages
    def process_dao(self, dao_msg):
        #add the node that has sent the dao message to the list of children of not already in the list
        if not ((dao_msg.sender.node_id, dao_msg.prefix) in self.children):
            self.children.append((dao_msg.sender.node_id, dao_msg.prefix))
        
        if not ((dao_msg.prefix, dao_msg.prefix) in self.routing_table):
            self.routing_table.append((dao_msg.prefix, dao_msg.prefix))
        
        for address in dao_msg.routing_table:
            if not ((dao_msg.prefix, address[1]) in self.routing_table):
                self.routing_table.append((dao_msg.prefix, address[1]))

        self.network.visualize(f'Node {self.node_id} processed DAO message from {dao_msg.sender.node_id}, at time {self.env.now}', self.node_id, dao_msg.sender.node_id, False, self.env.now)

        #forward DAO message up the DODAG
        if self.parent:
            self.env.process(self.send_dao())                                                    

    """
    Transmission functions
    """
    #LOOK MORE INTO THIS 
    def repair(self):
        self.rank += 10  # Increase rank to initiate local repair
        self.send_dio()  # Broadcast updated DIO message

    #trickle algorithm
    def trickle(self, I_min, I_max, k):
        I = I_min                               #minimum interval
        t = I / 2 + random.uniform(0, I / 2)    #determine random time between I_min/2 and I_min 

        #keep sending dis messages until I_max is reached: If max is reached then the least energy is used 
        while I <= I_max:
            yield self.env.timeout(t)       #wait for t time units i.e. node is idle/listening 
            if self.dio_count < k:          #node decides whether to transmit its own control message i.e DIS message if its counter is less than k (user-defined threshold)
                self.send_dis()
            
            #if no DIS messages are received within time interval, the interval is doubled for the next round in order to reduce the number of transmissions
            self.dio_count = 0
            I *= 2
            t = I / 2 + random.uniform(0, I / 2)