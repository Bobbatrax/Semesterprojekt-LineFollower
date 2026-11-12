import network
import socket
import time

SERVER_IP = "10.14.131.81"   # the ip printed by Pico 1

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Louis', 'n32t3c8xkmf9cky')

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
print('connected, ip=' + wlan.ifconfig()[0])

while True:
    try:
        c = socket.socket()
        c.connect((SERVER_IP, 80))
        c.send(b"GET\r\n")
        data = c.recv(64)
        print("Temperature:", data.decode(), "C")
        c.close()
    except OSError as e:
        print("error:", e)
    time.sleep(2)