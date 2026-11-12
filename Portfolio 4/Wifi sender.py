import network, rp2
rp2.country("DK")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
for ap in wlan.scan():
    print(ap[0], "| ch", ap[2], "| signal", ap[3])
    from machine import ADC
import network
import socket
import time

sensor = ADC(4)  # built-in temperature sensor

def read_temp():
    voltage = sensor.read_u16() * 3.3 / 65535
    return round(27 - (voltage - 0.706) / 0.001721, 1)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Louis', 'n32t3c8xkmf9cky')

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
print('connected, ip=' + wlan.ifconfig()[0])

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

while True:
    cl = None
    try:
        cl, addr = s.accept()
        cl.recv(1024)
        temp = str(read_temp())
        cl.send(temp)
        print("Sent: " + temp)
    except OSError as e:
        print('connection error', e)
    finally:
        if cl:
            cl.close()