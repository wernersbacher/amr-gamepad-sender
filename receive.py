import socket
localIP     = "0.0.0.0"
localPort   = 44000
bufferSize  = 128
msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

# Listen for incoming datagrams

while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0].decode("utf-8")

    clientMsg = "Message from Client: {} ".format(message)
    #clientIP  = "Client IP Address:{}".format(address)

    throttle, steering = message.split(",")
    
    print(f"throttle={throttle}, steering={steering}")
