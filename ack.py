#!/usr/bin/env python3

import serial
from digi.xbee.devices import *
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.models.address import XBee64BitAddress
from agent import Agent

ham = XBeeDevice('/dev/ttyUSB0', 57600)
ham.open()
xnet = ham.get_network()

agent_list = []
node_list = []

def millis():
        return round(time.time() * 1000)


def get_nodes_on_network():
        xnet.start_discovery_process()
        print("Grabbing Radios...")
        while xnet.is_discovery_running():
                time.sleep(0.5)
                nodes = xnet.get_devices()
        print("Done!")

# need to discover nodes before using them otherwise all remote agents will be 'None'
get_nodes_on_network()

def ack(data):
        node_id = ham.get_node_id()
        ham.send_data_broadcast(node_id + "-" + data)

def data_rcvd_callback(xbee_message):
        received = millis()
        address = xbee_message.remote_device.get_64bit_addr()
        node_id = xnet.get_device_by_64(address).get_node_id()
        data = xbee_message.data.decode("utf8")
        if(node_id == "ham5"):
                command(data)
        else:
                #print(str(node_id) + ", " + str(data) + ", " + str(received))
                store_fellow_agent_data(node_id, data, received)

# must be added after the defined rcvd callback function
ham.add_data_received_callback(data_rcvd_callback)
        

def command(data):
        if(data == "g"):
                transmit_default_data()


def transmit_default_data():
        for i in range(100):
                        time.sleep(0.1)
                        ham.send_data_broadcast(str("LATTLONGALTI"))

        time.sleep(2)
        calculate_average_message_transmission_per_remote_agent()

def store_fellow_agent_data(node_id, data, received):
        global agent_list
        global node_list

        remote_agent_message = (node_id, data, received)

        if (node_id not in node_list):
                node_list.append(node_id)
                new_agent = Agent(node_id, [remote_agent_message])
                agent_list.append(new_agent)
        else:
                find_agent(node_id).responses.append(remote_agent_message)

def find_agent(node_id):
        global agent_list

        for agent in agent_list:
                if (agent.node_id == node_id):
                        return agent


def calculate_average_message_transmission_per_remote_agent():
        global agent_list
        for agent in agent_list:
                average_response_time = (agent.responses[-1][2] - agent.responses[0][2]) / len(agent.responses)
                print(str(agent.node_id) + ", " + str(average_response_time) + "ms")

while True:
        z = input(">")


