import ShellyPy
import json
from datetime import datetime
import os
import schedule
import time

class Shelly:
    
    

    def __init__(self, ipadress:str) -> None:
        
        self.device = ShellyPy.Shelly(ipadress)
        



    def energy(self):

        return self.device.relay(0)["aenergy"]["total"]
    
    
    

   

     

    def read_json(self, filename):
        try:
            with open(filename, 'r') as file:
                # Check if the file is empty
                content = file.read()
                if not content:
                    return []

                # Parse JSON data
                data = json.loads(content)
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            print(f"Error decoding JSON in '{filename}': {e}")
            return []

    def write_json(self, filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)



    def update_and_write_json(self, filename, current_value):
        json_data = self.read_json(filename)

        if json_data and len(json_data) > 0:
            last_entry = json_data[-1]
            last_timestamp = last_entry.get('time')
            last_value = float(last_entry.get('total_watts'))
        else:
            last_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_value = 0.0  # Assuming a default value if the file is empty

        if last_timestamp:
            last_time = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            time_difference = (current_time - last_time).total_seconds()
        else:
            time_difference = 0.0

        # Calculate the subtraction
        subtraction_result = current_value - last_value

        # Add the current timestamp and value to the JSON data
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            'time': current_timestamp,
            'total_watts': current_value,
            'watts_during_time_interval': round(subtraction_result, 3),
            'time_interval': round(time_difference)
        }
        json_data.append(new_entry)

        # Write the updated JSON data back to the file
        self.write_json(filename, json_data)
        
        return json_data


    def run_hourly(self):
        # Schedule the function to run every hour
        def wrapper():
            self.update_and_write_json("shellyReadings.json", self.energy())
        
        schedule.every().minute.at(":00").do(wrapper)
        # Keep the program running
        while True:
            schedule.run_pending()
            time.sleep(1)
            


shellyIP = os.environ.get('ip', None)
laskuri = Shelly(shellyIP) #Put your shelly IP here
laskuri.run_hourly()
    
