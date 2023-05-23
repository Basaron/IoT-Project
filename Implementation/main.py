
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
 
    print("------------------------------Network created------------------------------")
    for node in network.nodes:
        print(f"Node {node.node_id} has position {node.position} and neighbors: {[n.node_id for n in node.neighbors]}")

    return network
    

#make a dodag from network 
def make_dodag(network):
        print("\n------------------------------Creation of DODAG------------------------------")
        #start simulation 
        network.start_simulation_dio(100)
        
        #printing the rank and parent of each node
        for node in network.nodes:
            print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")

        #visualize the network
        imageio.mimsave('output.gif', network.images, format='GIF', duration=500, loop = 1)
        
        #Remove the individual images after creating the GIF
        for i in range(len(network.images)):
            os.remove(f'output_{i}.png')


#-----------------SIMULATION---------------------#
if __name__ == "__main__":
    #make network
    network = test_auto_configure_network(8, 3, 10)

    #make dodag 
    make_dodag(network)




