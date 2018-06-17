import serial
import serial.tools.list_ports

# ser.close() 
Alpha = serial.tools.list_ports.comports()
print(len(Alpha))
for i in range(len(Alpha)):
    print(Alpha[i].device)


try:
    print("trying to connect to port 1")
    ser = serial.Serial('COM1',9600,timeout=5)
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
except:
    print("Could Not Connect")
    pass

try:
    print("trying to connect to port 2")
    ser = serial.Serial('COM9',9600,timeout=5)
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
except:
    print("Could nt connect")
    pass
# ser = serial.Serial('COM1',9600,timeout=5)
# ser.flushInput()

# while True:
#     try:
#         ser_bytes = ser.readline()
#         decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
#         print(decoded_bytes)
#     except:
#         print("Keyboard Interrupt")
#         break
        
