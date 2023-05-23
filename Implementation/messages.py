#-----------------CONTROL MESSAGES---------------------#
class DIO_Message:
    """
    DIO (DODAG Information Object) messages class:
    - Used for network discovery and configuration. 
    - Sent periodically or in response to a DIS message 
    - Shares information about the DODAG
    """
    def __init__(self, sender, rank):
        self.sender = sender
        self.rank = rank


class DIS_Message:
    """
    DIS (DODAG Information Solicitation) messages class:
    - Solicit DIO messages from its neighbors
    - Used when a new node in the network wants to join the DODAG
    - Requests information about the DODAG
    """
    def __init__(self, sender):
        self.sender = sender


class DAO_Message:
    """
    DAO (Destination Advertisement Object) messages class:
    - Propagates destination information upwards in the DODAG towards the root 
    - Helps to build the routing table and establish routes from the root to the leaves
    - 
    """
    def __init__(self, sender, prefix):
        self.sender = sender
        self.prefix = prefix