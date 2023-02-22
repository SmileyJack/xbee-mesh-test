class Agent:
    def __init__(self, node_id, responses):
        self.node_id = node_id
        self.responses = responses
        self.average_response_time = 0