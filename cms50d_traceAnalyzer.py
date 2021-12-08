import csv
import binascii
import matplotlib.pyplot as plt
import numpy as np

hr_values = []
spo2_values = []
pulse_byte1 = []
pulse_byte2 = []
pulse_byte1_bit67 = []
pulse_byte3 = []
pulse_byte4 = []
pulse_byte4_bit67 = []
hr_byte1 = []
hr_byte3 = []
hr_byte5 = []
hr_byte6 =[]


with open("C:\\Users\\nringels\PycharmProjects\\pythonCMD50D-BT\\reverse\\test_log_out_tom.csv", 'r') as input_file:
    csvreader = csv.DictReader(input_file)
    #header = next(csvreader)
    for row in csvreader:
        #print(row)
        if '0' == row['type']:
            pulse_byte1.append(int(row['byte1']) & 63)
            pulse_byte1_bit67.append((int(row['byte1']) >> 6)+10 )
            pulse_byte2.append(int(row['byte2']))
            pulse_byte3.append(int(row['byte3'])*100/15)
            pulse_byte4_bit67.append(int(row['byte4']) >> 6)
            print("pulse_byte1_bit67, pulse_byte4_bit67 : ", int(row['byte1']) >> 6, int(row['byte4']) >> 6)
            if 0 == (int(row['byte1']) >> 6):
                pulse_byte4.append(int(row['byte4'])) #0x3f
            else:
                pulse_byte4.append((int(row['byte4'])-64)%128)
        else:
            hr_byte1.append(int(row['byte1']))
            hr_values.append(int(row['byte2']))
            spo2_values.append(int(row['byte3']))
            hr_byte5.append(int(row['byte5']))
            hr_byte6.append(int(row['byte6']))


    #Plot Pulse
    time = np.arange(0, len(pulse_byte1)) * (1 / 60)
    # print("time: ",time)

    plt.plot(time, pulse_byte1, c='black',label="pulse_byte1_bit5-0")
    plt.plot(time, pulse_byte1_bit67, c='orange',label="pulse_byte1_bit6-7+10")
    plt.plot(time, pulse_byte2, c='red',label="pulse_byte2")
    plt.plot(time, pulse_byte3, c='green',label="pulse_byte3%")
    plt.plot(time, pulse_byte4_bit67, c='cyan',label="pulse_byte4_bit67")
    plt.plot(time, pulse_byte4, c='deeppink',label="pulse_byte4")

    plt.xlabel('Time (s)')
    plt.ylabel('Value')
    plt.legend()
    plt.show()


    """Format Pulse
    Byte0 = Header
    Byte1 = Type (0 = Pulse message)
    Byte2.bit0 = 
    Byte2.bit1 = 
    """