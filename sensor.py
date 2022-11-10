import wmi
import requests
from time import sleep

w = wmi.WMI(namespace="root\OpenHardwareMonitor")
while True:
    info = w.Sensor()
    for sensor in sorted(info, key=lambda x: (x.Name, x.SensorType)):
        if sensor.Name == "Memory" and sensor.SensorType == "Load":
            memory = round(sensor.Value) 
        elif sensor.Name == "CPU Total" and sensor.SensorType == "Load":
            cpu_load = round(sensor.Value) 
        elif sensor.Name == "CPU Package" and sensor.SensorType == "Temperature":
            cpu_temp = round(sensor.Value) 
        elif sensor.Name == "GPU Core" and sensor.SensorType == "Load":
            gpu_load = round(sensor.Value) 

    data = {
        "cpu_load": cpu_load,
        "cpu_temp": cpu_temp,
        "gpu_load": gpu_load,
        "memory": memory,
    }

    requests.post(url="http://192.168.2.211:5000/pc_request", json=data)
    sleep(30)