
from network import Network
import simpy
import random
import os 
import imageio


#make network based on random nodes 
def test_auto_configure_network(max_nodes, max_distance, area_size):
    env = simpy.Environment()
    network = Network(env)
    network.auto_configure(max_nodes, max_distance, area_size)

    assert len(network.nodes) == max_nodes           #check that the number of nodes created is equal to the max number of nodes specified
    
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
        network.start_simulation_dio(100)
        
        #printing the rank and parent of each node
        for node in network.nodes:
            print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")

        #visualize the network
        imageio.mimsave('output.gif', network.images, format='GIF', duration=500, loop = 1)
        
        #Remove the individual images after creating the GIF
        for i in range(len(network.images)):
            os.remove(f'output_{i}.png')


#adding a node to the network
def test_add_random_node(network, max_distance, area_size):

    #find the node in the network with highest node id
    max_node = max(network.nodes, key=lambda node: node.node_id)
    
    #add node with random position
    new_node = network.add_node(max_node.node_id + 1, (random.uniform(0, area_size), random.uniform(0, area_size)))

    #discover neighbors for the new node
    new_node.discover_neighbors(network, max_distance)

    #send dis, start simulation and update neighbours 
    network.start_simulation_dis(new_node, 200)
    network.update_dodag(max_distance)



    print("\n\n------------------------------Neighbours after new node is added------------------------------")

    for node in network.nodes:
        print(f"Node {node.node_id} has position {node.position} and neighbors: {[n.node_id for n in node.neighbors]}")

    print("\n\n------------------------------Rank and parent after new node is added------------------------------")
    for node in network.nodes:
            print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")

    


#removing a node from the network
#def test_remove_random_node():
     



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
    network = test_auto_configure_network(n_nodes, radius, area_size)

    

    #make dodag 
    test_make_dodag(network)


    """
    Test case 2 - Adding a node to the network
    """
    #add a node to the network
    test_add_random_node(network, radius, area_size)

    #make dodag
    #make_dodag(network, newNode=True)


    """
    Test case 3 - Removing a node from the network
    """




# add radius to the visualization 
#update rank and parent after adding a node