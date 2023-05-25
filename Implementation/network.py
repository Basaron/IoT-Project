import random
from node import Node
import matplotlib.pyplot as plt
import imageio
import os 

#-----------------NETWORK---------------------#
class Network:
    """
    Network class
    """
    def __init__(self, env):
        self.env = env
        self.nodes = []     #list of nodes in the network
        self.images = []    #list of images for GIF
        self.number_of_images = 0
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


    def update_dodag(self, max_distance):
        #update neighbours
        for node in self.nodes:
            node.discover_neighbors(self, max_distance)  # Node discovers its neighbors based on max distance



    def start_simulation_dio(self, simulation_time):
        #set root node rank 
        self.nodes[0].rank = 0
        self.images = [[]]*simulation_time
        # create a process for each node to send a DIO message    
        self.env.process(self.nodes[0].send_dio())
        self.env.run(until=simulation_time)
        self.save_plts_as_gif("DODAG.gif")


    def start_simulation_dis(self, new_node, simulation_time):
        self.images = [[]]*simulation_time
        #new node sends dis message
        self.env.process(new_node.send_dis())
        self.env.run(until=simulation_time)
        self.save_plts_as_gif("Add_node_dis.gif")
    
    #make an function that updates the DODAG i.e. the parent and children of each node, and the rank of each node, neightbors of each node


    def visualize(self, title, node_id_sender, node_reciver, send_msg, timestamp):        
        plt.figure(figsize=(self.area_size + 1, self.area_size + 1))
        plt.xlim(-1, self.area_size + 1)
        plt.ylim(-1, self.area_size + 1)
        plt.title(title, fontsize=20)
        for node in self.nodes:
            color = 'g' if node.rank == 0 else 'r' if node.rank > 50 else 'b'
            plt.scatter(*node.position, s=1000, c=color, zorder=3)  # Increase size by setting s
            plt.text(node.position[0], node.position[1], str(node.node_id), color='white', ha='center', va='center', fontsize=20)  # Add text
            if node.parent:
                plt.plot(*zip(node.position, node.parent.position), 'k-',zorder=1)

        if send_msg:
            dx = self.get_node(node_reciver).position[0] - self.get_node(node_id_sender).position[0]  # calculate difference in x 
            dy = self.get_node(node_reciver).position[1] - self.get_node(node_id_sender).position[1]  # calculate difference in y
            plt.arrow(self.get_node(node_id_sender).position[0], self.get_node(node_id_sender).position[1], dx, dy, zorder=5, color='g', 
            length_includes_head=True, head_width=0.4, head_length=0.3, width=0.05)
            

        filename = f'output_{self.number_of_images}.png'
        self.number_of_images += 1
        plt.savefig(filename)

        self.images[timestamp-1].append(imageio.v2.imread(filename))
        plt.close()


    def save_plts_as_gif(self, name):

        flat_list_of_images = [item for sublist in self.images for item in sublist]

        #visualize the network
        imageio.mimsave(name, flat_list_of_images, format='GIF', duration=500, loop = 1)
        
        #Remove the individual images after creating the GIF
        for i in range(self.number_of_images):
            os.remove(f'output_{i}.png')
        self.images.clear()
        self.number_of_images = 0
