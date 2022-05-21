import socket
import joystickapi
import msvcrt
import time

HZ = 20

UPPER_THRESHOLD = 32767
LOWER_THRESHOLD = -32768

DEADZONE = 5000


def convert_to_twist_range(x):
    if x >= UPPER_THRESHOLD:
        return 1.0
    
    if -DEADZONE < x < DEADZONE:
        return 0

    if 0 <= x < UPPER_THRESHOLD:
        return (x-DEADZONE)/(UPPER_THRESHOLD-DEADZONE)
        
    if LOWER_THRESHOLD < x < 0:
        return (x+DEADZONE)/(UPPER_THRESHOLD-DEADZONE)
        
    if x <= LOWER_THRESHOLD:
        return -1.0
    
    return 0



# socket things
serverAddressPort   = ("localhost", 44000)
bufferSize          = 128
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Send to server using created UDP socket

def send_inputs(throttle, steering):
    UDPClientSocket.sendto(str.encode(f"{throttle:.2f},{steering:.2f}"), serverAddressPort)


# init gamepad lib
num = joystickapi.joyGetNumDevs()
ret, caps, startinfo = False, None, None
for id in range(num):
    ret, caps = joystickapi.joyGetDevCaps(id)
    if ret:
        print("gamepad detected: " + caps.szPname)
        ret, startinfo = joystickapi.joyGetPosEx(id)
        break
else:
    print("no gamepad detected")
    exit()

run = ret

last_throttle = 0
last_steering = 0

while run:
    time.sleep(1/HZ)
    if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode(): # detect ESC
        run = False

    sendcommand = False
    ret, info = joystickapi.joyGetPosEx(id)
    if ret:
        steering = convert_to_twist_range(info.dwXpos-startinfo.dwXpos - 1)
        throttle = convert_to_twist_range(-(info.dwRpos-startinfo.dwRpos))
        
        if abs(steering-last_steering) > 0.02:
            print(f"steering changed to {steering}")
            last_steering = steering
            sendcommand = True
            
        if abs(throttle-last_throttle) > 0.02:
            print(f"throttle changed to {throttle}")
            last_throttle = throttle
            sendcommand = True

        if sendcommand:
            send_inputs(throttle=throttle, steering=steering)

            
            
socket.close()
print("end")

