import random
from node import Node
import matplotlib.pyplot as plt
import imageio

#-----------------NETWORK---------------------#
class Network:
    """
    Network class
    """
    def __init__(self, env):
        self.env = env
        self.nodes = []     #list of nodes in the network
        self.images = []    #list of images for GIF
        self.area_size = 0

    #add node to the network 
    def add_node(self, node_id, position):
        new_node = Node(self.env, self, node_id, position) #information: node id and position 
        self.nodes.append(new_node)
        return new_node

    #get node from the network
    def get_node(self, node_id):
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None
    

    """
    Simulation functions
    """
    #auto-configure network with randomly placed nodes
    def auto_configure(self, max_nodes, max_distance, area_size):
        self.area_size = area_size
        
        #adding random nodes in the network
        for i in range(max_nodes):
            position = (random.uniform(0, area_size), random.uniform(0, area_size))  # randomly generate position within area
            new_node = self.add_node(i, position)
        
        #discovering neighbors for each node
        for node in self.nodes:
            node.discover_neighbors(self, max_distance)  # Node discovers its neighbors based on max distance
    

    def start_simulation_dio(self, simulation_time):
        #set root node rank 
        self.nodes[0].rank = 0

        # create a process for each node to send a DIO message    
        self.env.process(self.nodes[0].send_dio())
        self.env.run(until=simulation_time)
    

    def visualize(self, title, node_id_sender, node_reciver, send_msg, makeGIF = True):
        if makeGIF:
            plt.figure(figsize=(self.area_size + 1, self.area_size + 1))
            plt.xlim(-1, self.area_size + 1)
            plt.ylim(-1, self.area_size + 1)
            for node in self.nodes:
                color = 'g' if node.rank == 0 else 'r' if node.rank > 50 else 'b'
                plt.scatter(*node.position, s=500, c=color, zorder=3)  # Increase size by setting s
                plt.text(node.position[0], node.position[1], str(node.node_id), color='white', ha='center', va='center')  # Add text
                if node.parent:
                    plt.plot(*zip(node.position, node.parent.position), 'k-',zorder=1)

            if send_msg:
                dx = self.get_node(node_reciver).position[0] - self.get_node(node_id_sender).position[0]  # calculate difference in x 
                dy = self.get_node(node_reciver).position[1] - self.get_node(node_id_sender).position[1]  # calculate difference in y
                plt.arrow(self.get_node(node_id_sender).position[0], self.get_node(node_id_sender).position[1], dx-0.2, dy-0.2, zorder=2, color='g', 
                length_includes_head=True, head_width=0.2, head_length=0.3)
                #plt.plot(*zip(self.get_node(node_id_sender).position, self.get_node(node_reciver).position), color='g')

            plt.title(title)
            filename = f'output_{len(self.images)}.png'
            plt.savefig(filename)
            self.images.append(imageio.v2.imread(filename))
            plt.close()
        

