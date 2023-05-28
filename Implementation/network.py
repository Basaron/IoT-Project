import random
from node import Node
import matplotlib.pyplot as plt
import imageio
import os 
import sys

#-----------------NETWORK---------------------#
class Network:
    """
    Network class
    """
    def __init__(self, env):
        self.env = env
        self.nodes = []             #list of nodes in the network
        self.images = []            #list of images for GIF
        self.num_all_msg =[]
        self.num_DIO_msg =[]
        self.num_DAO_msg =[]
        self.num_DIS_msg =[]
        self.number_of_images = 0
        self.area_size = 0
        self.I_min = 1              #minimum interval for Trickle algorithm
        self.I_max = 16             #maximum interval for Trickle algorithm
        self.k = 1                  #redundancy constant


    """
    Adder and Getter functions
    """
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
    def auto_configure(self, max_nodes, max_distance, area_size, network_selectd):
        self.area_size = area_size

        #seeds are based on autoconfigued networks 
        #seed 1: 7477812928102893072
        #seed 2: 4211468740914749448

        #make auto-configured network
        if network_selectd == 1:
            seed = 7477812928102893072          #run 
            rng = random.Random(seed)

            #adding random nodes in the network
            for i in range(max_nodes): 
                position = (rng.uniform(0, area_size), rng.uniform(0, area_size))  # randomly generate position within area
                self.add_node(i, position)    
        elif network_selectd == 2:
            seed = 4211468740914749448          #run 
            rng = random.Random(seed)

            #adding random nodes in the network
            for i in range(max_nodes): 
                position = (rng.uniform(0, area_size), rng.uniform(0, area_size))  # randomly generate position within area
                self.add_node(i, position)     
        elif network_selectd == 3:
            self.add_node(0, (5,5))
            self.add_node(1, (7,7))
            self.add_node(2, (3,3))
            self.add_node(3, (3,7))
            self.add_node(4, (7,3))
            self.add_node(5, (4,9))
            self.add_node(6, (5,1))
            self.add_node(7, (3,1))
            self.add_node(8, (1,5))
            self.add_node(9, (9,4))

        elif network_selectd == 4:
            self.add_node(0, (5,10))
            self.add_node(1, (3,8))
            self.add_node(2, (7,8))
            self.add_node(3, (7,6))
            self.add_node(4, (8,6))
            self.add_node(5, (6,6))
            self.add_node(6, (3,6))
            self.add_node(7, (4,6))
            self.add_node(8, (2,6))
            self.add_node(9, (1,4))
            self.add_node(10, (4,4))
            self.add_node(11, (6,4))
            self.add_node(12, (8,4))
            self.add_node(13, (9,4))
            self.add_node(14, (2,4))
            self.add_node(15, (3,4))
            self.add_node(16, (7,4))
            self.add_node(17, (5,2))
            self.add_node(18, (0,2))
            self.add_node(19, (10,2))
        else:
             print("Not a valid network selection")
            
            

        #discovering neighbors for each node
        for node in self.nodes:
            node.discover_neighbors(self, max_distance)  # Node discovers its neighbors based on max distance


    def update_neighbors(self, max_distance):
        #update neighbours
        for node in self.nodes:
            node.discover_neighbors(self, max_distance)  # Node discovers its neighbors based on max distance


    def setup_results(self, simulation_time):
        self.images = []
        self.num_msg =[0]*(simulation_time)
        self.num_DIO_msg =[0]*(simulation_time)
        self.num_DAO_msg =[0]*(simulation_time)
        self.num_DIS_msg =[0]*(simulation_time)


    def start_simulation_dio(self, simulation_time):
        #set root node rank 
        self.nodes[0].rank = 0
        self.setup_results(simulation_time)
        # create a process for each node to send a DIO message    
        self.env.process(self.nodes[0].send_dio())
        self.env.run(until=simulation_time)
        self.save_plts_as_gif("DODAG.gif", "DODAG_msg.png")


    def start_simulation_dis(self, new_node, simulation_time):
        self.setup_results(simulation_time)
        #new node sends dis message
        self.env.process(new_node.send_dis())
        self.env.run(until=simulation_time)
        self.save_plts_as_gif("Add_node_dis.gif", "Add_node_dis_msg.png")


    def start_simulation_trickle(self, simulation_time):
        self.nodes[0].rank = 0
        self.setup_results(simulation_time)
        self.env.process(self.nodes[0].trickle())   #start the Trickle algorithm for each node
        self.env.run(until=simulation_time)
        self.save_plts_as_gif("trickle.gif", "trickle.png")


    def start_simulation_trickle_repair(self, simulation_time, node_to_fail):
        self.nodes[0].rank = 0
        self.setup_results(simulation_time*3)
        print("--Time, node_id, I")
        self.env.process(self.nodes[0].trickle())   #start the Trickle algorithm for each node
        self.env.run(until=simulation_time)
        print("\n\n------------------------------Rank, Parent and Routing Table after DODAG ------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.get_node(node_to_fail).fail_node()

        self.env.run(until=simulation_time*2)
        print("\n\n------------------------------Rank, Parent and Routing Table after node is dead------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.get_node(node_to_fail).repair_node()
        self.env.run(until=simulation_time*3)
        print("\n\n------------------------------Rank, Parent and Routing Table after node repaired------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")


        self.save_plts_as_gif("trickle.gif", "trickle.png")


    def start_simulation_repair(self, node_to_fail):
        self.nodes[0].rank = 0
        self.setup_results(150)

        self.env.process(self.nodes[0].send_dio())
        self.env.run(until=50)

        print("\n\n------------------------------Rank, Parent and Routing Table after DODAG ------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        #self.save_plts_as_gif("repair_build.gif", "repair_build.png")
        self.get_node(node_to_fail).fail_node()
        
        self.env.run(until=100)
        print("\n\n------------------------------Rank, Parent and Routing Table after node is dead------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.get_node(node_to_fail).repair_node()
        self.env.run(until=150)
        print("\n\n------------------------------Rank, Parent and Routing Table after node repaired------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.save_plts_as_gif("repair.gif", "repair.png")


    """
    Visualization of the network
    """
    def visualize(self, title, node_id_sender, node_reciver, send_msg, timestamp, msg_type):
        timestamp = int(timestamp)
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
            if msg_type == 0:
                self.num_DIO_msg[timestamp-1] += 1
                self.num_msg[timestamp-1] += 1
            elif msg_type == 1:
                self.num_DAO_msg[timestamp-1] += 1
                self.num_msg[timestamp-1] += 1
            elif msg_type == 2:            
                self.num_DIS_msg[timestamp-1] += 1
                self.num_msg[timestamp-1] += 1
         
        """
        filename = f'output_{self.number_of_images}.png'
        self.number_of_images += 1
        plt.savefig(filename)
        self.images.append(imageio.v2.imread(filename))
        """
        plt.close()


    def save_plts_as_gif(self, name_gif, name_file):
        plt.title("Number of masseges", fontsize=20)
        plt.plot(self.num_msg, label='All msg')
        plt.plot(self.num_DIO_msg, label='DIO msg')
        plt.plot(self.num_DAO_msg, label='DAO msg')
        plt.plot(self.num_DIS_msg, label='DIS msg')
        plt.xlabel("Time")
        plt.ylabel("Msg")
        plt.legend()
        plt.savefig(name_file)
        plt.close()
        
        
        
        """
        #visualize the network
        imageio.mimsave(name_gif, self.images, format='GIF', duration=500, loop = 1)
        
        #Remove the individual images after creating the GIF
        for i in range(self.number_of_images):
            os.remove(f'output_{i}.png')
        """
        total_msg_num = 0
        DIO_msg_num = 0
        DAO_msg_num = 0
        DIS_msg_num = 0

        for i in range(len(self.num_msg)):
            total_msg_num += self.num_msg[i]
            DIO_msg_num += self.num_DIO_msg[i]
            DAO_msg_num += self.num_DAO_msg[i]
            DIS_msg_num += self.num_DIS_msg[i]

        print("Total msg count: ",total_msg_num)
        print("DIO msg count: ",DIO_msg_num)
        print("DAO msg count: ",DAO_msg_num)
        print("DIS msg count: ",DIS_msg_num)

        self.images.clear()
        self.number_of_images = 0
        self.num_msg.clear()
        self.num_DIO_msg.clear()
        self.num_DAO_msg.clear()
        self.num_DIS_msg.clear()

        
