import wmi
import requests

w = wmi.WMI(namespace="root\OpenHardwareMonitor")
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

