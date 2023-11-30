import ShellyPy
import csv
from datetime import datetime
import os


class Shelly:
    
    

    def __init__(self, ipadress:str) -> None:
        self.device = ShellyPy.Shelly(ipadress)



    def energy(self):

        return self.device.relay(0)["aenergy"]["total"]
    
    
    

   

     

    def read_csv(self, filename):
        with open(filename, 'r+') as file:
            reader = csv.reader(file)
            rows = list(reader)
            return rows



    def write_csv(self, filename, data):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)



    def update_and_write_csv(self, filename, current_value):
        # Read the existing CSV data
        csv_data = self.read_csv(filename)

        # Get the last value from the last row
        if csv_data:
            last_timestamp = csv_data[-1][0]
            last_value = float(csv_data[-1][-1])
        else:
            last_timestamp = None
            last_value = 0.0  # Assuming a default value if the file is empty

        # Calculate the subtraction
        subtraction_result = current_value - last_value

         # Add the current timestamp and value to the CSV data
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [current_timestamp, current_value]
        csv_data.append(new_row)

        

        # Write the updated CSV data back to the file
        self.write_csv(filename, csv_data)

        if last_timestamp:
            last_time = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            time_difference = (current_time - last_time).total_seconds()
        else:
            time_difference = 0.0

        return subtraction_result, time_difference

shellyIP = os.environ.get('ip', None)

laskuri = Shelly(shellyIP)

print(laskuri.update_and_write_csv("shellyReadings.csv", laskuri.energy()))