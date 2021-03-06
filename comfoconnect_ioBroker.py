import json
import sys
import argparse
import time
import requests

from pycomfoconnect import *

local_name = 'ioBroker'
local_uuid = bytes.fromhex('00000000000000000000000000000005')

sensor_data = {
    56: "",
    SENSOR_FAN_EXHAUST_FLOW: "",
    SENSOR_FAN_SUPPLY_FLOW: "",
    SENSOR_FAN_EXHAUST_SPEED: "",
    SENSOR_FAN_SUPPLY_SPEED: "",
    SENSOR_POWER_CURRENT: "",
    SENSOR_DAYS_TO_REPLACE_FILTER: "",
    SENSOR_TEMPERATURE_SUPPLY: "",
    SENSOR_BYPASS_STATE: "",
    SENSOR_TEMPERATURE_EXTRACT: "",
    SENSOR_TEMPERATURE_EXHAUST: "",
    SENSOR_TEMPERATURE_OUTDOOR: "",
    SENSOR_HUMIDITY_EXTRACT: "",
    SENSOR_HUMIDITY_EXHAUST: "",
    SENSOR_HUMIDITY_OUTDOOR: "",
    SENSOR_HUMIDITY_SUPPLY: "",
    SENSOR_FAN_NEXT_CHANGE: "",
}


def callback_sensor(sensor_id, sensor_value):
    sensor_data[sensor_id] = sensor_value


def discover_bridge(comfoconnect_ip):
    bridges = Bridge.discover(comfoconnect_ip)
    bridge = bridges[0] if bridges else None
    if bridge is None: 
        raise Exception("No bridges found!")
    return bridge


def register_sensors(comfoconnect): 
    comfoconnect.register_sensor(56)  # Operation mode
    comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_FLOW)  # Temperature & Humidity: Supply Air (temperature)
    comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_FLOW)  # Fans: Supply fan flow
    comfoconnect.register_sensor(SENSOR_FAN_EXHAUST_SPEED)  # Fans: Exhaust fan speed
    comfoconnect.register_sensor(SENSOR_FAN_SUPPLY_SPEED)  # Fans: Supply fan speed
    comfoconnect.register_sensor(SENSOR_FAN_SPEED_MODE)  # Fans: User Setting
    comfoconnect.register_sensor(SENSOR_POWER_CURRENT)  # Power Consumption: Current Ventilation
    comfoconnect.register_sensor(SENSOR_DAYS_TO_REPLACE_FILTER)  # Days left before filters must be replaced
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_SUPPLY)  #  Temperaturee Supply
    comfoconnect.register_sensor(SENSOR_BYPASS_STATE)  # Bypass state
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    comfoconnect.register_sensor(SENSOR_TEMPERATURE_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_EXTRACT)  # Temperature & Humidity: Extract Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_EXHAUST)  # Temperature & Humidity: Exhaust Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_OUTDOOR)  # Temperature & Humidity: Outdoor Air (temperature)
    comfoconnect.register_sensor(SENSOR_HUMIDITY_SUPPLY)  # Temperature & Humidity: Supply Air (temperature)
    comfoconnect.register_sensor(SENSOR_FAN_NEXT_CHANGE)  # General: Countdown until next fan speed change


def retrieve_sensor_data_for_seconds(comfoconnect, seconds): 
    while seconds > 0 :
        # Callback messages will arrive in the callback method.
        time.sleep(1)
        seconds = seconds - 1
        if not comfoconnect.is_connected():
            break


def connect_to_comfoconnect(comfoconnect_ip, comfoconnect_pin): 
    bridge = discover_bridge(comfoconnect_ip)
    comfoconnect = ComfoConnect(bridge, local_uuid, local_name, comfoconnect_pin)
    comfoconnect.callback_sensor = callback_sensor 
    comfoconnect.connect(False)  # Disconnect existing clients.
    return comfoconnect


def run_comfoconnect_handler(comfoconnect_ip, comfoconnect_pin):
    comfoconnect = connect_to_comfoconnect(comfoconnect_ip, comfoconnect_pin)
    register_sensors(comfoconnect)  
    retrieve_sensor_data_for_seconds(comfoconnect, 5)   
    comfoconnect.disconnect()   


#def extract_pin(data):
#    if not data["params"]:
#        raise Exception("""
#        No PIN as parameter defined!
#        Make sure to pass arguments in sensor settings in following format:
#        "<pin>". E.g: "9432"
#        """)
#    pin = data["params"].split(" ")[0]
#    return pin
    

def set_ventilation_stage_message(ventilation_stage): 
    msg = ""
    if ventilation_stage == 0:
        msg = "Außer Haus"
    elif ventilation_stage in (1, 2, 3): 
        msg = f"Lüftungsstufe: {ventilation_stage}"
    return msg


def set_operation_message(operation): 
    msg = ""
    if operation == -1:
        msg = "Betrieb: Automatik"
    elif operation == 1:
        msg = "Betrieb: Manuell"
    return msg


def set_status_message(operation, ventilation_stage): 
    ventilation_stage_msg = set_ventilation_stage_message(ventilation_stage)
    operation_msg = set_operation_message(operation)
    msg = f"{operation_msg} | {ventilation_stage_msg}"
    return msg


if __name__ == "__main__":
    try:
        #data = json.loads(sys.argv[1])
        
        comfoconnect_ip = "" # ip-address of comfoconnect lan-c
        comfoconnect_pin = "0000" # Pin needs to be defined in sensor settings: "Additonal parameters: <pin>", default is 0
        ioBroker = "" #ip-address:port of iobroker
        dp = "Zehnder.0."
        
        # Gets all the data
        run_comfoconnect_handler(comfoconnect_ip, comfoconnect_pin) 
        
        # Status Message is depending on the values of the operation and ventilation stage sensors
        #csr = CustomSensorResult(text=f"{set_status_message(sensor_data[56], sensor_data[SENSOR_FAN_SPEED_MODE])}")
        text=f"{set_status_message(sensor_data[56], sensor_data[SENSOR_FAN_SPEED_MODE])}"
        print(text)
        url = "http://" + ioBroker + "/set/" + dp + "Modus?value=" + set_operation_message(sensor_data[56])
        print(url)
        with open('zehnder.json', 'w', encoding = 'utf-8') as f:  # writing JSON object
                    
            data = { "Zeit" : time.time()}
            
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Letztes_Update?value=" + str(time.time()))
            
            data = {"name" : "Betriebsmodus",
                        "value" : set_operation_message(sensor_data[56]),
                        "unit" : "Modus"}
            json.dump(data, f, ensure_ascii=False) 
            response = requests.get(url)
            print(response)            
        
            data = {"name" : "Lüftungsstufe",
                        "value" : sensor_data[SENSOR_FAN_SPEED_MODE],
                        "unit" : "Stufe",
                        "is_limit_mode" : True,
                        "limit_min_warning" : -0.1,
                        "limit_max_warning" : 3.1}  
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Stufe?value=" + str(sensor_data[SENSOR_FAN_SPEED_MODE]))
            print(response)
        
            data = {"name" : "Volumen Fortluftventilator",
                        "value" : sensor_data[SENSOR_FAN_EXHAUST_FLOW],
                        "unit" : "m³/h",
                        "is_limit_mode" : True,
                        "limit_min_warning" : 40}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Ventilator.Volumen_Fortluft?value=" + str(sensor_data[SENSOR_FAN_EXHAUST_FLOW]))
        
            data = {"name" : "Volumen Zuluftventilator",
                        "value" : sensor_data[SENSOR_FAN_SUPPLY_FLOW],
                        "unit" : "m³/h",
                        "is_limit_mode" : True,
                        "limit_min_warning" : 40}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Ventilator.Volumen_Zuluft?value=" + str(sensor_data[SENSOR_FAN_SUPPLY_FLOW]))
            
            data = {"name" : "Drehzahl Fortluftventilator",
                        "value" : sensor_data[SENSOR_FAN_EXHAUST_SPEED],
                        "unit" : "rpm"}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Ventilator.Drehzahl_Fortluft?value=" + str(sensor_data[SENSOR_FAN_EXHAUST_SPEED]))
        
            data = {"name" : "Drehzahl Zuluftventilator",
                        "value" : sensor_data[SENSOR_FAN_SUPPLY_SPEED],
                        "is_limit_mode" : True,
                        "limit_min_error" : 1, 
                        "limit_error_msg" : "Ventilator steht!",
                        "unit" : "rpm"}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Ventilator.Drehzahl_Zuluft?value=" + str(sensor_data[SENSOR_FAN_SUPPLY_SPEED]))
        
            data = {"name" : "Energieverbrauch Lüftung",
                        "value" : sensor_data[SENSOR_POWER_CURRENT],
                        "unit" : "Watt"}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Energieverbrauch?value=" + str(sensor_data[SENSOR_POWER_CURRENT]))
        
            data = {"name" : "Restlaufzeit Filter",
                        "value" : sensor_data[SENSOR_DAYS_TO_REPLACE_FILTER],
                        "unit" : "Tage",
                        "is_limit_mode" : True,
                        "limit_min_error" : 10, 
                        "limit_min_warning" : 30,
                        "limit_error_msg" : "Filterwechsel dringend",
                        "limit_warning_msg" : "Filterwechsel demnächst"}                
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Restlaufzeit_Filter?value=" + str(sensor_data[SENSOR_DAYS_TO_REPLACE_FILTER]))
            
            data = {"name" : "Status Bypass",
                        "value" : sensor_data[SENSOR_BYPASS_STATE],
                        "unit" : "%"}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Bypass?value=" + str(sensor_data[SENSOR_BYPASS_STATE]))
        
            data = {"name" : "Temperatur Zuluft",
                        "value" : sensor_data[SENSOR_TEMPERATURE_SUPPLY]/10,
                        "is_float" : True,
                        "unit" : "°C",
                        "is_limit_mode" : True,
                        "limit_min_warning" : -10,
                        "limit_min_error" : -20,
                        "limit_max_warning" : 50,
                        "limit_max_error" : 60}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Temperatur.Zuluft?value=" + str(sensor_data[SENSOR_TEMPERATURE_SUPPLY]))
        
            data = {"name" : "Temperatur Abluft",
                        "value" : sensor_data[SENSOR_TEMPERATURE_EXTRACT]/10,
                        "is_float" : True,
                        "unit" : "°C",
                        "is_limit_mode" : True,
                        "limit_min_warning" : -10,
                        "limit_min_error" : -20,
                        "limit_max_warning" : 50,
                        "limit_max_error" : 60}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Temperatur.Abluft?value=" + str(sensor_data[SENSOR_TEMPERATURE_EXTRACT]))
        
            data = {"name" : "Temperatur Fortluft",
                        "value" : sensor_data[SENSOR_TEMPERATURE_EXHAUST]/10,
                        "is_float" : True,
                        "unit" : "°C",
                        "is_limit_mode" : True,
                        "limit_min_warning" : -10,
                        "limit_min_error" : -20,
                        "limit_max_warning" : 50,
                        "limit_max_error" : 60}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Temperatur.Fortluft?value=" + str(sensor_data[SENSOR_TEMPERATURE_EXHAUST]))
       
            data = {"name" : "Temperatur Außenluft",
                        "value" : sensor_data[SENSOR_TEMPERATURE_OUTDOOR]/10,
                        "is_float" : True,
                        "unit" : "°C",
                        "is_limit_mode" : True,
                        "limit_min_warning" : -10,
                        "limit_min_error" : -20,
                        "limit_max_warning" : 50,
                        "limit_max_error" : 60}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Temperatur.Außenluft?value=" + str(sensor_data[SENSOR_TEMPERATURE_OUTDOOR]))
        
            data = {"name" : "Feuchtigkeit Abluft",
                        "value" : sensor_data[SENSOR_HUMIDITY_EXTRACT],
                        "unit" : "%",
                        "is_limit_mode" : True,
                        "limit_min_warning" : 30,
                        "limit_min_error" : 20,
                        "limit_max_warning" : 60,
                        "limit_max_error" : 70}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Feuchtigkeit.Abluft?value=" + str(sensor_data[SENSOR_HUMIDITY_EXTRACT]))
        
            data = {"name" : "Feuchtigkeit Fortluft",
                        "value" : sensor_data[SENSOR_HUMIDITY_EXHAUST],
                        "unit" : "%"}
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Feuchtigkeit.Fortluft?value=" + str(sensor_data[SENSOR_HUMIDITY_EXHAUST]))
        
            data = {"name" : "Feuchtigkeit Außenluft",
                        "value" : sensor_data[SENSOR_HUMIDITY_OUTDOOR],
                        "unit" : "%"}                        
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Feuchtigkeit.Außenluft?value=" + str(sensor_data[SENSOR_HUMIDITY_OUTDOOR]))
        
            data = {"name" : "Feuchtigkeit Zuluft",
                        "value" : sensor_data[SENSOR_HUMIDITY_SUPPLY],
                        "unit" : "%"}                               
            json.dump(data, f, ensure_ascii=False)
            response = requests.get("http://" + ioBroker + "/set/" + dp + "Feuchtigkeit.Zuluft?value=" + str(sensor_data[SENSOR_HUMIDITY_SUPPLY]))
    
            data = {"name" : "Zeit bis Änderung Ventilatorstufe",
                        "value" : sensor_data[SENSOR_FAN_NEXT_CHANGE],
                        "unit" : "h"}                               
            json.dump(data, f, ensure_ascii=False)
            #response = requests.get("http://" + ioBroker + "/set/" + dp + "Zeit_Lüfter_Änderung?value=" + str(sensor_data[SENSOR_FAN_NEXT_CHANGE]))
            
    except Exception as e:
        print(e)
