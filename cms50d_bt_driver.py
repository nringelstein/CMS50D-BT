"""
Async callbacks with a queue and external consumer
--------------------------------------------------
An example showing how async notification callbacks can be used to
send data received through notifications to some external consumer of
that data.
Created on 2021-02-25 by hbldh <henrik.blidh@nedomkull.com>
"""
import sys
import time
import platform
import asyncio
import logging
import keyboard

#TEST
import csv

output_file = open("C:\\Users\\nringels\PycharmProjects\\pythonCMD50D-BT\\reverse\\test_log_out.csv", 'w', newline='')
# create the csv writer
fieldnames = ['timestamp', 'header','type','byte1','byte2','byte3','byte4','byte5','byte6']
writer = csv.DictWriter(output_file,fieldnames=fieldnames)
writer.writeheader()

#CMS50D-BT Message Protocol format
CMS_LIVEDATA_PACKET_HEADER = 235 #0xEB
CMS_PULSE_WAVE_MSG_ID = 0   #0x00
CMS_HR_SPO2_MSG_ID    = 1   #0x01
CMS_PULSE_WAVE_MSG_LENGTH = 6
CMS_HR_SPO2_MSG_LENGTH = 8


from bleak import BleakClient

logger = logging.getLogger(__name__)

ADDRESS = (
    "F6:18:6B:FB:F7:00"
)

running_flag = True
msg_buffer = bytearray()
msg_decoded = bytearray()

async def run_ble_client(address: str, queue: asyncio.Queue):
    global running_flag

    async def callback_handler(sender, data):
        await queue.put((time.time(), data))


    async with BleakClient(address) as client:
        logger.info(f"Connected: {client.is_connected}")
        await client.start_notify("0000ff02-0000-1000-8000-00805f9b34fb", callback_handler)
        await client.start_notify("0000ff04-0000-1000-8000-00805f9b34fb", callback_handler)

        await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x81\x01'), response=False)
        await asyncio.sleep(0.5)
        await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x82\x02'), response=False)
        await asyncio.sleep(0.5)
        await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x9a\x1a'), response=False)
        await asyncio.sleep(0.5)
        await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x9b\x00\x1b'), response=False)
        await asyncio.sleep(1.0)
        await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x9b\x01\x1c'), response=False)

        #wait for 30s
        while True == running_flag:
            await asyncio.sleep(5.0)
            await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x9a\x1a'), response=False)

        #Stop streaming data
        await client.write_gatt_char("0000ff01-0000-1000-8000-00805f9b34fb", bytearray(b'\x9b\x7f\x1a'), response=False)

        # Send an "exit command to the consumer"
        await queue.put((time.time(), None))


def process_livedata(epoch, data):
    global msg_buffer

    msg_buffer += data

    # Handle the case, partial message received in the livedata stream
    i = 0
    while i < len(msg_buffer):
        msg_decoded = bytearray()
        # New message decoded
        if CMS_LIVEDATA_PACKET_HEADER == msg_buffer[i]:
            if CMS_PULSE_WAVE_MSG_ID == msg_buffer[i + 1] and CMS_PULSE_WAVE_MSG_LENGTH <= len(msg_buffer):
                msg_decoded = msg_buffer[i:CMS_PULSE_WAVE_MSG_LENGTH]
                # Pop out the message from the msg buffer
                msg_buffer = msg_buffer[CMS_PULSE_WAVE_MSG_LENGTH:]
                i = 0  # Reset counter since message popped out
            elif CMS_HR_SPO2_MSG_ID == msg_buffer[i + 1] and CMS_HR_SPO2_MSG_LENGTH <= len(msg_buffer):
                msg_decoded = msg_buffer[i:CMS_HR_SPO2_MSG_LENGTH]
                # Pop out the message from the msg buffer
                msg_buffer = msg_buffer[CMS_HR_SPO2_MSG_LENGTH:]
                i = 0  # Reset counter since message popped out
            # Check if one message has been successfully decoded
            if 0 < len(msg_decoded):
                ['timestamp', 'header', 'type', 'byte1', 'byte2', 'byte3', 'byte4', 'byte5', 'byte6']
                msg = list(msg_decoded)
                if 0 == msg[1]:
                    writer.writerow({'timestamp': str(epoch), 'header':msg[0], 'type':msg[1],'byte1':msg[2], 'byte2':msg[3], 'byte3':msg[4], 'byte4':msg[5]})
                else:
                    writer.writerow({'timestamp': str(epoch), 'header':msg[0], 'type':msg[1],'byte1':msg[2], 'byte2':msg[3], 'byte3':msg[4], 'byte4':msg[5], 'byte5':msg[6], 'byte6':msg[7]})
                #print('DECODED : ', msg_decoded.hex().upper())
            else:
                # Step out loop since no complete message remaining in the buffer
                break
        else:
            # pop out the element
            msg_buffer = msg_buffer[i + 1:]



async def run_queue_consumer(queue: asyncio.Queue):
    global running_flag
    while True:
        # Use await asyncio.wait_for(queue.get(), timeout=1.0) if you want a timeout for getting data.
        epoch, data = await queue.get()

        if data is None:
            logger.info(
                "Got message from client about disconnection. Exiting consumer loop..."
            )
            break
        else:
            logger.info(f"Received callback data via async queue at {epoch}: {data}")
            process_livedata(epoch, data )

        # press 'q' to exit
        if keyboard.is_pressed("q"):
            output_file.close()
            running_flag = False


async def main(address: str):
    queue = asyncio.Queue()
    client_task = run_ble_client(address, queue)
    consumer_task = run_queue_consumer(queue)
    await asyncio.gather(client_task, consumer_task)
    logger.info("Main method done.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else ADDRESS
        )
    )