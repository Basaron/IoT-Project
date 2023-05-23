
from network import Network
import simpy
import random


def test_auto_configure_nodes_creation(max_nodes, max_distance, area_size, makeDodag = True):
    env = simpy.Environment()
    network = Network(env)
    network.auto_configure(max_nodes, max_distance, area_size)

    assert len(network.nodes) == max_nodes           #check that the number of nodes created is equal to the max number of nodes specified
    
    for node in network.nodes:
        assert 0 <= node.position[0] <= area_size    #x-coordinate of node is within the expected range
        assert 0 <= node.position[1] <= area_size    #y-coordinate of node is within the expected range

    #print the number of neighbors for each node    
    print("------------------------------Network created------------------------------")
    for node in network.nodes:
        print(f"Node {node.node_id} has position {node.position} and neighbors: {[n.node_id for n in node.neighbors]}")
    
    if makeDodag:
        print("\n------------------------------Creation of DODAG------------------------------")
        #set random root node from array of nodes
        root_node = random.choice(network.nodes)
        root_node.rank = 0
        root_node.parent = None
        root_node.send_dio()
        








#-----------------SIMULATION---------------------#
if __name__ == "__main__":
    #make network without dodag
    test_auto_configure_nodes_creation(10, 5, 20, makeDodag=False)

    #make network with dodag
    test_auto_configure_nodes_creation(10, 5, 20, makeDodag=True)
    
    
"""
  #----------------------Test: DIO message test to form DODAG----------------------
    print("\nTest DIO")
    msgCount = 0
    node1.rank = 0             #set root node
    node1.send_dio()           #send DIO message to all neighbors from root 

    #env.process(node1.send_dio())

    #sim_duration = 1000                                #run the simulation for 20 time units
    #env.run(until=sim_duration)


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
"""