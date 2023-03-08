class Agent:
    def __init__(self, node_id, responses):
        self.node_id = node_id
        self.responses = responses # intended to be list of tuples of length 3. responses[0][0] = node_id, responses [0][1] = data, responses[0][2] = time elapsed to respond
        self.average_response_time = 0
        self.altitude = 0
        self.lattitude = 0
        self.longitude = 0
        self.last_received = 0
        self.current_received = 0
        self.time_between_locations = 0