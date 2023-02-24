class Agent:
    def __init__(self, node_id, responses):
        self.node_id = node_id
        self.responses = responses
        self.average_response_time = 0
        self.altitude = 0
        self.lattitude = 0
        self.longitude = 0