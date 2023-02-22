#!/usr/bin/env python3

import serial
from digi.xbee.devices import *
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.models.address import XBee64BitAddress
from agent import Agent

response_log = dict()
send_log = dict()
agent_list = []

ground = XBeeDevice('/dev/tty.usbserial-D306E1ZP', 57600)
ground.open()
xnet = ground.get_network()

def millis():
    return round(time.time() * 1000)

def get_nodes_on_network():
    xnet.start_discovery_process()
    print("Grabbing Radios...")
    while xnet.is_discovery_running():
        time.sleep(0.5)
    nodes = xnet.get_devices()
    print("Done!")

get_nodes_on_network()


def data_rcvd_callback(xbee_message):
    received = millis()
    address = xbee_message.remote_device.get_64bit_addr()
    node_id = xnet.get_device_by_64(address).get_node_id()
    data = xbee_message.data.decode("utf8")
    calculate_and_record_message_and_response_time(data, received, node_id)


def calculate_and_record_message_and_response_time(data, received, node_id):
    global response_log
    global send_log
    global agent_list

    split_id_from_message = data.split("-")

    response_time = received - send_log.get(int(split_id_from_message[1]))

    new_response_from_agent = (data, response_time)
    print(new_response_from_agent)

    if (node_id not in response_log.keys()):
        new_agent = Agent(node_id, [new_response_from_agent])
        response_log[node_id] = new_agent
        agent_list.append(new_agent)

    else:
        current_list_of_responses = response_log.get(node_id).responses
        current_list_of_responses.append(new_response_from_agent)

def grab_average_agent_response_time():
    global agent_list

    for agent in agent_list:
        sum = 0
        for num_records in range(len(agent.responses)):
             sum += agent.responses[num_records][1]
        agent.average_response_time = sum / len(agent.responses)

ground.add_data_received_callback(data_rcvd_callback)

def main():
    global send_log
    global response_log
    global agent_list

    for i in range(10):
        print(i)
        ground.send_data_broadcast(str(i))
        sent = millis()
        send_log[i] = sent

    time.sleep(2)
    grab_average_agent_response_time()
    for agent in agent_list:
        print(str(agent.node_id) + " " + str(agent.average_response_time))
    #print(response_log.get("ham1").responses)


if __name__ == "__main__":
    main()
