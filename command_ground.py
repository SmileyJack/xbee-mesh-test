#!/usr/bin/env python3

import serial
from digi.xbee.devices import *
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.models.address import XBee64BitAddress
from agent import Agent

response_log = dict()
send_log = dict()
agent_list = []

ground = XBeeDevice('/dev/tty.usbserial-D306E1YO', 57600)
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

def poll_network():
    node_ids = []
    nodes = xnet.get_connections()

    for node in nodes:
        node_ids.append(node.get_node_id())

    print(node_ids)


def data_rcvd_callback(xbee_message):
    received = millis()
    address = xbee_message.remote_device.get_64bit_addr()
    node_id = xnet.get_device_by_64(address).get_node_id()
    data = xbee_message.data.decode("utf8")
    # calculate_and_record_message_and_response_time(data, received, node_id)


def calculate_and_record_message_and_response_time(data, received, node_id):
    global response_log
    global send_log
    global agent_list

    split_id_from_message = data.split("-")

    response_time = received - send_log.get(int(split_id_from_message[1]))

    new_response_from_agent = (data, response_time)

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

def show_ui():
    print("Remote agent commands:")
    print("(a) Begin transmission")
    print("(b) Crash into a tree")
    print("(c) Deliver me Taco Bell")
    print("(d) View nodes on network")

def request_input():
    begin_transmission_command = "g"
    crash_into_tree_command = "c"
    deliver_taco_bell_command = "t"

    send = input("Send information? (y/n) ")
    while send == 'y':
        show_ui()
        choice = input("(e) Refresh network\n")

        if (choice.lower() == 'a'):
            ground.send_data_broadcast(begin_transmission_command)

        elif (choice.lower() == 'b'):
            send_data_and_display_time_to_send(crash_into_tree_command)

        elif (choice.lower() == 'c'):
            send_data_and_display_time_to_send(deliver_taco_bell_command)

        elif (choice.lower() == 'd'):
            poll_network()

        elif (choice.lower() == 'e'):
            get_nodes_on_network()

        else:
            print("Enter a valid choice")

        send = input("Send more information? (y/n) ")

def main():
    global send_log
    global response_log
    global agent_list

    while True:
        request_input()
    
    


if __name__ == "__main__":
    main()
