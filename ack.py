#!/usr/bin/env python3

import serial
from digi.xbee.devices import *
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.models.address import XBee64BitAddress

ham = XBeeDevice('/dev/ttyUSB1', 57600)
ham.open()

xnet = ham.get_network()

def get_nodes_on_network():
        xnet.start_discovery_process()
        print("Grabbing Radios...")
        while xnet.is_discovery_running():
                time.sleep(0.5)
                nodes = xnet.get_devices()
        print("Done!")

get_nodes_on_network()

def ack(data):
        node_id = ham.get_node_id()
        ham.send_data_broadcast(node_id + "-" + data)

def data_rcvd_callback(xbee_message):
        address = xbee_message.remote_device.get_64bit_addr()
        node_id = xnet.get_device_by_64(address).get_node_id()
        data = xbee_message.data.decode("utf8")
        print(node_id)
        if(node_id == "ham2"):
                ack(data)


ham.add_data_received_callback(data_rcvd_callback)

while True:
        z = input(">")


