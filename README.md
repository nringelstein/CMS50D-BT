# CMS50D-BT
BLE Client to oximeter CMS50D-BT device
The objective of this project is to connect to a CMS50D-BT device, and retrieve data.
At this stage, I'm sharing a preliminary implementation following hacking of the device.
Content:
- cms50d_bt_driver.py file allows to capture SpO2, HR (@1 Hz) and Pulse signal (@60 Hz)
- cms50d_trace_analyzer.py allows to plot the pulse signal (for debug)
