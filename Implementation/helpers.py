from network import Network
import random
import sys
import matplotlib.pyplot as plt
import simpy

#find 10 different seeds for 10 different networks

def find_good_networks(network, max_nodes, area_size):
    x = 0

    network.area_size = area_size

    #make 10 plots 
    for i in range(10):
        seed = random.randrange(sys.maxsize)
        rng = random.Random(seed)
        
        for i in range(max_nodes): 
            position = (rng.uniform(0, network.area_size), rng.uniform(0, network.area_size))  # randomly generate position within area
            network.add_node(i, position)    
        

        plt.figure(figsize=(network.area_size + 1, network.area_size + 1))
        plt.xlim(-1, network.area_size + 1)
        plt.ylim(-1, network.area_size + 1)
        plt.title("test", fontsize=20)

        for node in network.nodes:
            color = 'g' if node.rank == 0 else 'r' if node.rank > 50 else 'b'
            plt.scatter(*node.position, s=1000, c=color, zorder=3)  # Increase size by setting s
            plt.text(node.position[0], node.position[1], str(node.node_id), color='white', ha='center', va='center', fontsize=20)  # Add text
            if node.parent:
                plt.plot(*zip(node.position, node.parent.position), 'k-',zorder=1)

        plt.savefig(str(x))
        print(x, seed)
        plt.close()
        network.nodes.clear()
        x += 1


if __name__ == "__main__":
    env = simpy.rt.RealtimeEnvironment(factor=1, strict=False)
    network = Network(env)
    n_nodes = 10
    area_size = 10

    find_good_networks(network, n_nodes, area_size)


    