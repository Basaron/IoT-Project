
from network import Network
import simpy
import random


#make network based on random nodes 
def test_auto_configure_network(max_nodes, max_distance, area_size, auto):
    env = simpy.rt.RealtimeEnvironment(factor=1, strict=False)
    network = Network(env)
   
    network.auto_configure(max_nodes, max_distance, area_size, auto)
    

    #assert len(network.nodes) == max_nodes           #check that the number of nodes created is equal to the max number of nodes specified
    
    for node in network.nodes:
        assert 0 <= node.position[0] <= area_size    #x-coordinate of node is within the expected range
        assert 0 <= node.position[1] <= area_size    #y-coordinate of node is within the expected range

    #check if root node has neighbours - run test again:
    if len(network.nodes[0].neighbors) == 0:
        print("Root node has no neighbors. Please try again")
        exit()

    print("\n\n------------------------------Network created------------------------------")
    for node in network.nodes:
        print(f"Node {node.node_id} has position {node.position} and neighbors: {[n.node_id for n in node.neighbors]}")

    return network
    

#make a dodag from network 
def test_make_dodag(network):
    print("\n\n------------------------------Creation of DODAG------------------------------")
    #send dio and start simulation 
    network.start_simulation_dio(10)
    
    #printing the rank and parent of each node
    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
        print(f"Node {node.node_id} route table: {node.routing_table}")
    


#adding a node to the network
def test_add_random_node(network, max_distance, area_size):

    #find the node in the network with highest node id
    max_node = max(network.nodes, key=lambda node: node.node_id)
    
    #add node with random position
    new_node = network.add_node(max_node.node_id + 1, (random.uniform(0, area_size), random.uniform(0, area_size)))

    #discover neighbors for the new node
    new_node.discover_neighbors(network, max_distance)

    #send dis, start simulation and update neighbours 
    network.start_simulation_dis(new_node, 20)
    #network.update_dodag(max_distance)

    print("\n\n------------------------------Neighbours after new node is added------------------------------")

    for node in network.nodes:
        print(f"Node {node.node_id} has position {node.position} and neighbors: {[n.node_id for n in node.neighbors]}")

    print("\n\n------------------------------Rank and parent after new node is added------------------------------")
    for node in network.nodes:
            print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
            print(f"Node {node.node_id} route table: {node.routing_table}")
    
def test_trickle():

    sim_duration = 50
    network.start_simulation_trickle(sim_duration)

    #printing the rank and parent of each node
    for node in network.nodes:
        print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
        print(f"Node {node.node_id} route table: {node.routing_table}")

#removing a node from the network
def test_remove_and_repair_node(network):
    network.start_simulation_repair()
     



#-----------------SIMULATION---------------------#
if __name__ == "__main__":
    #parameters
    n_nodes = 10
    radius = 3
    area_size = 10

    """
    Test case 1 - Making a simple DODAG network based on random nodes
    """
    #make network
    network = test_auto_configure_network(n_nodes, radius, area_size, True)

    #make dodag 
    test_make_dodag(network)

    """
    Test case 2 - Adding a node to the network
    """
    #add a node to the network
    #test_add_random_node(network, radius, area_size)

    #make dodag
    #make_dodag(network, newNode=True)


    """
    Test case 3 - Removing a node from the network
    """
    #test_remove_and_repair_node(network)

    """
    Test case 4 - test trickle
    """
    #test_trickle()




# add radius to the visualization 
#update rank and parent after adding a node