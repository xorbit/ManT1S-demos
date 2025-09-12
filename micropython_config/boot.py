# This file is executed on every boot (including wake-boot from deepsleep)
import machine
import network
import requests
import time
import webrepl

# Configure LAN
lan = network.LAN(mdc = machine.Pin(8), mdio = machine.Pin(7),
                  power = None, phy_type = network.PHY_LAN8670, phy_addr=0)

# LAN active already? It could be active after soft reboot
if lan.active():
    # Deactivate so we can update the hostname if needed
    lan.active(False)

# If an ipaddress file is present and valid, it overrides DHCP
# You need to manually configure an IP address if not connected to a network
# with a DHCP server
try:
    with open('/ipaddress') as f:
        ipaddress = f.readline().strip()
    lan.ipconfig(addr4=ipaddress)
except:
    lan.ipconfig(dhcp4=True)

# Set hostname, from file if present, auto generated otherwise
# This allows you to communicate with the ManT1S board by name instead of
# IP address if you use the ManT1S-Bridge and your router supports it
try:
    with open('/hostname') as f:
        hostname = f.readline().strip()
    network.hostname(hostname)
except:
    hostname = (f'mant1s-'
        f'{(int.from_bytes(lan.config("mac")[-4:],"big")>>2)&0xFFFFFF:06x}')
    network.hostname(hostname)

# Activate LAN
lan.active(True)

# Print the device's IP address to the console
print (f"Hostname is {network.hostname()}")

# Start webrepl
webrepl.start()
