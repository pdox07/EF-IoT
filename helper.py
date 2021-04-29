from scrape import *

ref_dict = {}
cl = []

def status(is_on):
    if is_on:
        return "ON"
    else:
        return "OFF"

def get_device_ip(device_name):
    global ref_dict
    global cl
    if device_name in ref_dict.keys():
        return ref_dict[device_name]
    else:
        cl,ref_dict = get_dhcp_list()
        return ref_dict[device_name]


