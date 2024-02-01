"""
Created on Wed Jan  3 16:47:07 2024

@author: HP
"""

import json

def generate_config(json_data, output_dir):
    
    for AS in json_data.keys():
        
        for router, config in json_data[AS]['routers'].items():
            
            with open(f"{output_dir}/{router}_config.cfg", 'w') as file:

                debut_cfg(file,router)

                for interface in config['interfaces']:
                    file.write("!\n")
                    file.write(f"interface {interface['interfaceName']}\n")
                    start_interface(file, interface)
                    file.write(f" ipv6 address {interface['ipAddress']}\n")
                    file.write(" no shutdown\n")
                    if 'RIP' in config:
                        file.write (f" ipv6 rip {config['RIP']['process_name']} enable \n")
                    if 'OSPF' in config:
                        ospf_config = config['OSPF']
        
                        area_id = ospf_config['area']
                        
                        file.write(f" ipv6 ospf 1 area {area_id}\n")
                        file.write("!\n"*3)
                        #file.write(f" ipv6 ospf cost {interface['ospfCost']} \n")
                        file.write("!\n")

                if 'RIP' in config:
                    asn = json_data[AS]['autonomousSystem']
                    
                    file.write("!\n"*3)
                    file.write(f"ipv6 router rip {config['RIP']['process_name']} \n")
                    file.write(" redistribute connected\n")
                    file.write(f" redistribute bgp {asn} include-connected \n")
                    file.write("!\n")
                    #file.write("exit")
                
                    
                        #file.write(f" ipv6 ospf cost {interface['ospfCost']} \n")
                    

                if 'OSPF' in config:
                    ospf_config = config['OSPF']
                    file.write("ipv6 router ospf 1\n")
                    file.write(f" router-id {ospf_config['routeurId']}\n")
                    file.write(" log-adjacency-changes \n")
                    if 'iBGP' in config:
                        asn = json_data[AS]['autonomousSystem']
                        file.write(f" redistribute bgp {asn} include-connected \n")
                    file.write("\n"*3)
                        #file.write("exit")
                    
                    #file.write("exit\n")

                if 'iBGP' in config:
                    asn = json_data[AS]['autonomousSystem']
                    bgp_id=config['iBGP']['routeurId']
                    file.write(f"router bgp {asn}\n")
                    file.write(" bgp log-neighbor-changes\n")
                    file.write(f" bgp router-id {bgp_id} \n")
                    
                    for peer in config['iBGP']['peers']:
                        file.write(f" neighbor {peer} remote-as {asn}\n")

                    if 'eBGP' in config:
                        asn_d = json_data[AS]['autonomousSystem']
                        conf_ebgp = dict(config['eBGP'])
                        
                        for neighbor, dico in conf_ebgp.items():
                            #print(neighbor)
                            asn_a = dico['remoteAsn']
                            
                            for neighbor_ip in dico['ipAddress']:
                                file.write(f" neighbor {neighbor_ip} remote-as {asn_a}\n")
                        file.write(" no auto-summary \n")
                        file.write(" !\n")

                        file.write(" address-family ipv6 unicast\n")
                        
                        for neighbor, dico in conf_ebgp.items():
                            for neighbor_ip in dico['ipAddress']:
                                file.write(f" neighbor {neighbor_ip} activate\n")
                        
                        if 'RIP' in config:
                            file.write(f" redistribute rip {config['RIP']['process_name']} ")
                            file.write("no synchronization")
                        if 'OSPF' in config:
                            file.write(" redistribute ospf 1 match internal external 1 external 2\n")
                        file.write(f" network {config['iBGP']['address']}\n")
                        file.write(" exit-address-family \n")
                        file.write("!\n"*2)
                        file.write("no ip http server\nno ip http secure-server\n!\n!\nno cdp log mismatch duplex\n")


                    file.write("!\n")
                        
                    file.write("!\n"*2)
                        
                
                        
                        
                        #file.write("exit\n")


                    file.write("\n")
                fin_cfg(file)


def debut_cfg(file, router):
    file.write("! \nversion 12.4 \nservice timestamps debug datetime msec \nservice timestamps log datetime msec \nno service password-encryption\n")
    file.write("! \n")
    file.write(f"hostname {router}\n!\n")
    file.write("! \n")
    file.write("boot-start-marker \nboot-end-marker \n! \n! \nno aaa new-model \nno ip icmp rate-limit unreachable\n! \n! \nip cef\nno ip domain lookup\n!\n!")
    file.write("!\n"*4)
    file.write("ipv6 unicast-routing \n")  
    file.write("!\n"*4)
    file.write("ip tcp synwait-time 5\n")
    file.write("!\n")

def start_interface(file, interface):
    file.write(" no ip address\n duplex auto\n speed auto\n")

def fin_cfg(file):
    file.write("!\n"*4)
    file.write("control-plane\n")
    file.write("!\n"*4)
    file.write("gatekeeper\n shutdown\n")
    file.write("!\n"*2)
    file.write("line con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\n")
    file.write("!\n"*2)
    file.write("end")
# Example usage
json_file = "corrected_test_1.json"
output_directory = "./"

with open(json_file, 'r') as file:
    data = json.load(file)

generate_config(data, output_directory)