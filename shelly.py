import ShellyPy
import json
from datetime import datetime
import os
import schedule
import time
import requests



class Shelly:
    
    

    def __init__(self, name:str, ipadress:str) -> None:
        
        self.device = ShellyPy.Shelly(ipadress)
        self.name = name
        
        



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
            return
        
   


    def write_json(self, filename, data):
        with open(filename, 'w') as file:
            json.dump(data, file, indent=2)



    def update_and_write_json(self, filename, current_value):
        json_data = self.read_json(filename)

        if json_data and len(json_data) > 0:
            last_entry = json_data[-1]
            last_timestamp = last_entry.get('time')
            last_value = float(last_entry.get('total_watts'))
            last_cost = float(last_entry.get('total_cost'))
        else:
            last_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_value = current_value  # Assuming a default value if the file is empty
            last_cost = 0.0 # Assuming a default if the file is empty

        if last_timestamp:
            last_time = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            time_difference = (current_time - last_time).total_seconds()
        else:
            time_difference = 0.0

        
            

        # Calculate the subtraction
        subtraction_result = current_value - last_value

        # Calculate the electricity cost
        
        price_data = self.read_json("lastHour.json")
        if price_data:
            price = price_data.get('PriceWithTax')
            cost = (subtraction_result/1000) * price
        else:
            cost = 0.0

        if time_difference > 3605:
            cost = 0.0
        #calculate total cost
        
        total_cost =+ last_cost + cost


        # Add the current timestamp and value to the JSON data
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_entry = {
            'time': current_timestamp,
            'total_watts': current_value,
            'watts_during_time_interval': round(subtraction_result, 3),
            'time_interval': round(time_difference),
            'price_during_time_interval': round(cost, 3),
            'total_cost': round(total_cost, 3)
        }
        json_data.append(new_entry)
        print(self.name, new_entry)
        
        # Write the updated JSON data back to the file
        self.write_json(filename, json_data)
        
        return json_data

    def get_price(self):
        try:
            response = requests.get("https://api.spot-hinta.fi/JustNow")
            if response.status_code == 200:
                response_json = response.json()
                self.write_json("lastHour.json", response_json)
            else:
                print(f"Error: Request failed with status code {response.status_code}")
        except requests.RequestException as e:
            # Handle other request-related exceptions
            print(f"Error: {e}")
            

    def run_hourly(self):
        # Schedule the function to run every hour
        def update_wrapper():
           
            self.update_and_write_json(self.name+".json", self.energy())
        
        def price_wrapper():

            self.get_price()
            
        
        schedule.every().minute.at(":00").do(update_wrapper)

        schedule.every().minute.at(":10").do(price_wrapper)
        
 
            


if __name__ == "__main__":
    settings_file_path = os.path.join(os.path.dirname(__file__), 'settings.json')

    with open(settings_file_path, 'r') as file:
        content = file.read()
        data = json.loads(content)

    
    for shelly_data in data.get('shellies', []):
        name = shelly_data.get('name')
        ip_address = shelly_data.get('ip')
        print(f"Creating instance for {name} with IP {ip_address}")
        sheldon = Shelly(name, ip_address)
        sheldon.run_hourly()
        




    while True:
        schedule.run_pending()
        time.sleep(1)


    




    
