import socket
import joystickapi
import msvcrt
import time

HZ = 20

UPPER_THRESHOLD = 32767
LOWER_THRESHOLD = -32768

DEADZONE = 5000


GEARS = [0.27, 0.29, 0.3, 0.32, 0.35, 0.4, 0.7, 1.0]
BACKWARDS_GEAR = 0.23
MAX_GEAR = len(GEARS)

def get_gear_factor(gear: int) -> float:
    if gear > MAX_GEAR:
        gear = MAX_GEAR
    elif gear < 1:
        gear = 1
    return GEARS[gear-1]

def inc_max(num, max_num):
    return min(num+1, max_num)

def dec_min(num, min_num):
    return max(num-1, min_num)

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
    UDPClientSocket.sendto(str.encode(f"{throttle:.4f},{steering:.4f}"), serverAddressPort)


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

current_gear = 1

old_r1 = False
old_l1 = False

while run:
    time.sleep(1/HZ)
    if msvcrt.kbhit() and msvcrt.getch() == chr(27).encode(): # detect ESC
        run = False

    sendcommand = False
    ret, info = joystickapi.joyGetPosEx(id)
    if ret:
        # buttons auslesen
        btns = [(1 << i) & info.dwButtons != 0 for i in range(caps.wNumButtons)]
        l1, r1 = btns[4], btns[5]
                
        # hoch und runterschalten, bedinungen an button knüpfen
        if r1 and not old_r1:
            current_gear = inc_max(current_gear, MAX_GEAR)
            sendcommand = True
        if l1 and not old_l1:
            current_gear = dec_min(current_gear, 1)
            sendcommand = True
        
        old_l1, old_r1 = l1, r1

        # gas und lenkung auslesen
        steering = convert_to_twist_range(info.dwXpos-startinfo.dwXpos - 1) 
        # convert right stick to speed
        throttle = convert_to_twist_range(-info.dwRpos+startinfo.dwRpos)
        
        # if driving forward, apply gearing
        if throttle > 0:
            throttle *= get_gear_factor(current_gear)  
        else: # only one backward speed!
            throttle *= BACKWARDS_GEAR
            
        # schauen ob neue werte gesendet werden sollen
        if abs(steering-last_steering) > 0.002:
            last_steering = steering
            sendcommand = True
            
        if abs(throttle-last_throttle) > 0.002:
            last_throttle = throttle
            sendcommand = True
 
        if sendcommand:
            send_inputs(throttle=throttle, steering=steering)
            print(f"gear={current_gear}____throttle={throttle:.4f}_____steering={steering:.4f}_____", end="\r")
           

            
            
socket.close()
print("end")

