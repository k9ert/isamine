
import requests
import random
import goodwe
import time
import datetime


power_switch_ip = "192.168.178.172"
solar_ip = '192.168.1.14'

max_switch_time_milli = 4000
last_switch_time = 0


def can_toggle_based_on_time_interval():
    global last_switch_time
    current_time_milli = time.time() * 1000  # Get current time in milliseconds
    
    # Check if enough time has passed since the last switch
    if (current_time_milli - last_switch_time) < max_switch_time_milli:
        print("Switching too soon. Waiting for the max switch time to pass.")
        return False
    return True

def is_within_allowed_time_window():
    # Check current hour to ensure it's between 10 AM (inclusive) and 4 PM (exclusive)
    current_hour = datetime.datetime.now().hour
    if not(10 <= current_hour < 16):
        print("Currently outside the allowed time window (10 AM to 4 PM). Toggling not allowed.")
        return False
    return True



def mine_switcher():
    # We don't want to toggle too often
    if not can_toggle_based_on_time_interval():
        return
    
    # Fetch the current mining state (update get_report() accordingly)
    currently_mining = get_report()
    
    print("Currently mining: " + str(currently_mining))
    toggle_power(should_we_mine(currently_mining))
    
def toggle_power(yes_or_no):
    state = "1" if yes_or_no else "0"
    url = f"http://{power_switch_ip}/relay?state=" + state
    
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")


def should_we_mine(currently_mining):
    should_mine = currently_mining
    if not is_within_allowed_time_window():
        should_mine = False
    else:
        should_mine = not currently_mining
    
    if (should_mine != currently_mining):
        global last_switch_time  # Update the last switch time after toggling
        last_switch_time = time.time() * 1000  # Update to current time in milliseconds
    return should_mine

def get_report():
    url = f'http://{power_switch_ip}/report'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            return data["relay"]
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error making request to {url}: {e}")

def get_battery_soc():
    control_output = get_control_output()
    lines = control_output.split("\n") 
    for line in lines: 
        if "battery_soc" in line: 
            soc = line.split("=")[1].strip().split(" ")[0] 
            return int(soc) 
        return None


def get_control_output():
    return """
vpv1:            PV1 Voltage = 0.0 V
ipv1:            PV1 Current = 0.0 A
ppv1:            PV1 Power = 0 W
pv1_mode:                PV1 Mode code = 0 
pv1_mode_label:                  PV1 Mode = PV panels not connected 
vpv2:            PV2 Voltage = 371.9 V
ipv2:            PV2 Current = 0.6 A
ppv2:            PV2 Power = 223 W
pv2_mode:                PV2 Mode code = 1 
pv2_mode_label:                  PV2 Mode = PV panels connected, no power 
ppv:             PV Power = 223 W
vbattery1:               Battery Voltage = 53.4 V
battery_status:                  Battery Status = 80 
battery_temperature:             Battery Temperature = 23.8 C
ibattery1:               Battery Current = 11.1 A
pbattery1:               Battery Power = 593 W
battery_charge_limit:            Battery Charge Limit = 78 A
battery_discharge_limit:                 Battery Discharge Limit = 78 A
battery_error:           Battery Error Code = 0 
battery_soc:             Battery State of Charge = 70 %
battery_soh:             Battery State of Health = 102 %
battery_mode:            Battery Mode code = 2 
battery_mode_label:              Battery Mode = Discharge 
battery_warning:                 Battery Warning = 0 
meter_status:            Meter Status code = 1 
vgrid:           On-grid Voltage = 231.3 V
igrid:           On-grid Current = 3.5 A
pgrid:           On-grid Export Power = 0 W
fgrid:           On-grid Frequency = 50.0 Hz
grid_mode:               Work Mode code = 1 
grid_mode_label:                 Work Mode = Inverter On 
vload:           Back-up Voltage = 231.3 V
iload:           Back-up Current = 0.1 A
pload:           On-grid Power = 800 W
fload:           Back-up Frequency = 50.0 Hz
load_mode:               Load Mode code = 1 
load_mode_label:                 Load Mode = The inverter is connected to a load 
work_mode:               Energy Mode code = 2 
work_mode_label:                 Energy Mode = Normal (On-Grid) 
temperature:             Inverter Temperature = 29.7 C
error_codes:             Error Codes = 0 
e_total:                 Total PV Generation = 5703.1 kWh
h_total:                 Hours Total = 12579 h
e_day:           Today's PV Generation = 5.0 kWh
e_load_day:              Today's Load = 6.5 kWh
e_load_total:            Total Load = 3762.7 kWh
total_power:             Total Power = 788 W
effective_work_mode:             Effective Work Mode code = 1 
effective_relay_control:                 Effective Relay Control = 48 
grid_in_out:             On-grid Mode code = 0 
grid_in_out_label:               On-grid Mode = Idle 
pback_up:                Back-up Power = 0 W
plant_power:             Plant Power = 800 W
meter_power_factor:              Meter Power Factor = 0.001 
diagnose_result:                 Diag Status Code = 33554496 
diagnose_result_label:           Diag Status = Discharge Driver On, PF value set 
house_consumption:               House Consumption = 816 W
"""

async def get_runtime_data():
    inverter = await goodwe.connect(solar_ip)
    runtime_data = await inverter.read_runtime_data()

    for sensor in inverter.sensors():
        if sensor.id_ in runtime_data:
            print(f"{sensor.id_}: \t\t {sensor.name} = {runtime_data[sensor.id_]} {sensor.unit}")
