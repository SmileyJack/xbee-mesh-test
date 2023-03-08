#!/usr/bin/env python3

import serial
from digi.xbee.devices import *
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.models.address import XBee64BitAddress
from agent import Agent

ham = XBeeDevice('/dev/ttyUSB0', 57600)
ham.open()
xnet = ham.get_network()

# agent list is a list of all other agents. Local agent is not in its own list
agent_list = []

# Only used to determine if an agent already exists in agent list in attempt to not have to compare agent objects
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


# def ack(data):
#     node_id = ham.get_node_id()
#     ham.send_data_broadcast(node_id + "-" + data)


def data_rcvd_callback(xbee_message):
    received = millis()
    address = xbee_message.remote_device.get_64bit_addr()
    node_id = xnet.get_device_by_64(address).get_node_id()
    data = xbee_message.data.decode("utf8")
    # ham5 was the ground control for all testing
    if (node_id == "ham5"):
        command(data)

    # must be remote agent
    else:
        # print(str(node_id) + ", " + str(data) + ", " + str(received))
        store_remote_agent_data(data, received)


# must be added after the defined rcvd callback function
ham.add_data_received_callback(data_rcvd_callback)


def command(data):
    if (data == "g"):
        transmit_default_data()

# Adam parsing function

def parse_remote_agent_location(data):
    # parse incoming string...
    # agent strings start with 'a'
    if (data[0] == 'a'):

        # reset the index
        idx = 1
        temp_str = ''

        # grab the id number, by stacking chars until we reach a colon :
        while (data[idx] != ':'):
            temp_str += data[idx]
            idx += 1

        id = int(temp_str)

        # reset our temporary string so we can add new characters
        temp_str = ''

        # increment idx so we go past the 'y' in the
        # received string
        idx += 2

        while (data[idx] != 'x'):
            temp_str += data[idx]
            idx += 1
        lon = float(temp_str)
        temp_str = ''

        idx += 1
        while (data[idx] != 'a'):
            temp_str += data[idx]
            idx += 1
        lat = float(temp_str)

        temp_str = ''

        idx += 1
        while (idx < len(data)):
            temp_str += data[idx]
            idx += 1
        alt = float(temp_str)

        return id, lon, lat, alt


# Sends location to all other agents
def transmit_default_data():
    for i in range(100):
        time.sleep(0.1)
        ham.send_data_broadcast("a" + ham.get_node_id()
                                [-1] + ":y141.000x-96.000a2.00")

    time.sleep(2)
    calculate_average_message_transmission_per_remote_agent()


def store_remote_agent_data(data, received):
    global agent_list
    global node_list

    id, lon, lat, alt = parse_remote_agent_location(data)
    remote_agent_message = (id, data, received)

    # creating new agent and filling it with cool jazz
    if (id not in node_list):
        node_list.append(id)
        new_agent = Agent(id, [remote_agent_message])
        new_agent.longitude = lon
        new_agent.lattitude = lat
        new_agent.altitude = alt
        new_agent.last_received = new_agent.current_received
        new_agent.current_received = received
        new_agent.time_between_locations = new_agent.current_received - new_agent.last_received
        agent_list.append(new_agent)
    else:
        # if the agent already exists in global agent list, 
        update_agent_location(id, lon, lat, alt, received, remote_agent_message)

def update_agent_location(id, lon, lat,  alt, received, remote_agent_message):
    global agent_list

    for agent in agent_list:
        if (id == agent.node_id):
            agent.longitude = lon
            agent.lattitude = lat
            agent.altitude = alt
            agent.last_received = agent.current_received
            agent.current_received = received
            agent.time_between_locations = agent.current_received - agent.last_received
            agent.responses.append(remote_agent_message)
            print(agent.node_id, agent.time_between_locations)
            break


# def find_agent(node_id):
#     global agent_list

#     for agent in agent_list:
#         if (agent.node_id == node_id):
#             return agent


def calculate_average_message_transmission_per_remote_agent():
    global agent_list
    for agent in agent_list:

        # accesses the list of tuples that is 'responses' to calculate avg time
        average_response_time = (
            agent.responses[-1][2] - agent.responses[0][2]) / len(agent.responses)
        print(str(agent.node_id) + ", " + str(average_response_time) + "ms")
        print(agent.longitude,agent.lattitude,agent.altitude)


# def print_out_local_agent_data(agent):
#     for x in agent.responses:
#         print(x[1])
    
#     print(agent.id, agent.lon, agent.lat, agent.alt)



while True:
    z = input(">")
