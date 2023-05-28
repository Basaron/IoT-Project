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
    def auto_configure(self, max_nodes, max_distance, area_size, auto):
        self.area_size = area_size

        #seeds are based on autoconfigued networks 
        #seed 1: 7477812928102893072
        #seed 2: 4211468740914749448

        #make auto-configured network
        if auto:
            seed = 4211468740914749448          #run 
            rng = random.Random(seed)

            #adding random nodes in the network
            for i in range(max_nodes): 
                position = (rng.uniform(0, area_size), rng.uniform(0, area_size))  # randomly generate position within area
                self.add_node(i, position)    
                
            """
            #find 10 different seeds for 10 different networks
            for i in range(10):
                seed = random.randrange(sys.maxsize)
                rng = random.Random(seed)
                
                for i in range(max_nodes): 
                    position = (rng.uniform(0, area_size), rng.uniform(0, area_size))  # randomly generate position within area
                    self.add_node(i, position)    
                

                plt.figure(figsize=(self.area_size + 1, self.area_size + 1))
                plt.xlim(-1, self.area_size + 1)
                plt.ylim(-1, self.area_size + 1)
                plt.title("test", fontsize=20)

                for node in self.nodes:
                    color = 'g' if node.rank == 0 else 'r' if node.rank > 50 else 'b'
                    plt.scatter(*node.position, s=1000, c=color, zorder=3)  # Increase size by setting s
                    plt.text(node.position[0], node.position[1], str(node.node_id), color='white', ha='center', va='center', fontsize=20)  # Add text
                    if node.parent:
                        plt.plot(*zip(node.position, node.parent.position), 'k-',zorder=1)

                plt.savefig(str(x))
                print(x, seed)
                plt.close()
                self.nodes.clear()
                x += 1
                """


 
        #use manual network 
        else:
            """
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
            """

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
            

        #discovering neighbors for each node
        for node in self.nodes:
            node.discover_neighbors(self, max_distance)  # Node discovers its neighbors based on max distance


    def update_neighbors(self, max_distance):
        #update neighbours
        for node in self.nodes:
            node.discover_neighbors(self, max_distance)  # Node discovers its neighbors based on max distance


    def setup_results(self, simulation_time):
        self.images = [[]]*(simulation_time)
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
        print("--Time, node_id, I")
        self.env.process(self.nodes[0].trickle())   #start the Trickle algorithm for each node
        self.env.run(until=simulation_time)
        self.save_plts_as_gif("trickle.gif", "trickle.png")


    def start_simulation_trickle_repair(self, simulation_time):
        self.nodes[0].rank = 0
        self.setup_results(simulation_time*3)
        print("--Time, node_id, I")
        self.env.process(self.nodes[0].trickle())   #start the Trickle algorithm for each node
        self.env.run(until=simulation_time)
        print("\n\n------------------------------Rank, Parent and Routing Table after DODAG ------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.get_node(2).fail_node()

        self.env.run(until=simulation_time*2)
        print("\n\n------------------------------Rank, Parent and Routing Table after node is dead------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.get_node(2).repair_node()
        self.env.run(until=simulation_time*3)
        print("\n\n------------------------------Rank, Parent and Routing Table after node repaired------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")


        self.save_plts_as_gif("trickle.gif", "trickle.png")


    def start_simulation_repair(self):
        self.nodes[0].rank = 0
        self.setup_results(60)

        self.env.process(self.nodes[0].send_dio())
        self.env.run(until=20)

        print("\n\n------------------------------Rank, Parent and Routing Table after DODAG ------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        #self.save_plts_as_gif("repair_build.gif", "repair_build.png")
        self.get_node(4).fail_node()
        
        """
        #made example
        self.env.process(self.nodes[0].send_dio())
        self.env.process(self.nodes[6].send_dio())
        self.env.process(self.nodes[7].send_dio())
        self.env.process(self.nodes[8].send_dio())
        self.env.process(self.nodes[4].send_dio())
        self.env.process(self.nodes[3].send_dio())
        #big tree and seed 1
        self.env.process(self.nodes[0].send_dio())
        self.env.process(self.nodes[4].send_dio())
        self.env.process(self.nodes[3].send_dio())
        self.env.process(self.nodes[5].send_dio())
        self.env.process(self.nodes[7].send_dio())
        """ 
        
        #seed2
        self.env.process(self.nodes[7].send_dio())
        self.env.process(self.nodes[4].send_dio())
        
        
        self.env.run(until=40)
        print("\n\n------------------------------Rank, Parent and Routing Table after node is dead------------------------------")
        for node in self.nodes:
                print(f"Node {node.node_id} rank: {node.rank}, and parent: {node.parent.node_id if node.parent else None} ")
                print(f"Node {node.node_id} route table: {node.routing_table}")

        self.get_node(4).repair_node()
        self.env.run(until=60)
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
         
        filename = f'output_{self.number_of_images}.png'
        self.number_of_images += 1
        plt.savefig(filename)
        #self.images[timestamp-1].append(imageio.v2.imread(filename))
        
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
        
        
        flat_list_of_images = [item for sublist in self.images for item in sublist]
        """
        #visualize the network
        imageio.mimsave(name_gif, flat_list_of_images, format='GIF', duration=500, loop = 1)
        
        #Remove the individual images after creating the GIF
        for i in range(self.number_of_images):
            os.remove(f'output_{i}.png')
        """
        total_msg_num = 0
        for i in  self.num_msg:
             total_msg_num += i
        print("Total msg count: ",total_msg_num)

        self.images.clear()
        self.number_of_images = 0
        self.num_msg.clear()
        self.num_DIO_msg.clear()
        self.num_DAO_msg.clear()
        self.num_DIS_msg.clear()

        
