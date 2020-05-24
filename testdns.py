import socket
import dnslib

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = dnslib.DNSRecord.question("vk.com")
socket.sendto(data.pack(), ('localhost', 53))
socket.close()
