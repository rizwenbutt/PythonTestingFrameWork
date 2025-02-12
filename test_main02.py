import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def find_sequences(filename):
    #function to extract the registration numbers in the file by finding all capital in the correct format
    pattern = re.compile(r'\b[A-Z]{2}\d{2}[A-Z]{3}\b|\b[A-Z]{2}\d{2} [A-Z]{3}\b')
    
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = pattern.findall(content)
    
    return {"filename": filename, "matches": matches}

def process_file(input_filename, output_filename):
    results = find_sequences(input_filename)
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        if results["matches"]:
            #output_file.write("Found sequences:\n")
            for match in results["matches"]:
                output_file.write(match + "\n")
        else:
            output_file.write("No matching sequences found.\n")
    
    print(f"Results have been written to {output_filename}")
    return results


def load_car_data(file_path):
 #create a dictioary with key by reg for use with the expected results file
    car_data = {}
    
    # Read the CSV file
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        # Iterate over each row in the CSV file
        for row in csv_reader:
            variant_reg = row['VARIANT_REG']
            make_model = row['MAKE_MODEL']
            year = row['YEAR']
            
            # Store the data in the dictionary
            car_data[variant_reg] = {
                'MAKE_MODEL': make_model,
                'YEAR': year
            }
    
    return car_data

def get_car_details(car_data, variant_reg):
    #call to get data and check if found for expected result
    return car_data.get(variant_reg, "Variant registration not found")


if __name__ == "__main__":
    input_filename = r"C:\\Users\\rizwe\\Downloads\\input.txt"  # Updated file path
    output_filename = r"C:\\Users\\rizwe\\Downloads\\output.txt"
    
    result_dict = process_file(input_filename, output_filename)
     # Loop through all registration numbers
    for variant_reg in result_dict['matches']:
        print(f"Testing registration: {variant_reg}")
        #print (result_dict['matches'][0])

class TestCarReg:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        

    def test_car_reg(self):
        driver = self.driver
        driver.get("https://motorway.co.uk")

        input_filename = r"C:\\Users\\rizwe\\Downloads\\input.txt"   # File path of input file
        output_filename = r"C:\\Users\\rizwe\\Downloads\\output.txt" # New output file saved for debugging with all the found registration numbers
       
       #save results into dictionary and also to an output file 
        result_dict = process_file(input_filename, output_filename)
        for variant_reg in result_dict['matches']:
        #Send the first number plate to the website and click submit

                numberplate = driver.find_element(By.ID, "vrm-input")
                numberplate.clear()  # Clear input before entering new data
                #numberplate.send_keys(result_dict['matches'][0])
                numberplate.send_keys(variant_reg)
                submit = driver.find_element(By.CLASS_NAME, "Button-module__label-SKEy")
                submit.click()
                    
        # time.sleep(5)
        # Use an explicit wait to wait for results from website and save to expected result for acutal make and actual year
                try:
                    actual_make = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1[data-cy='vehicleMakeAndModel']"))
                    ).text
                                
                    actual_year = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//ul[@data-cy='vehicleSpecifics']/li[1]"))
                    ).text
                
                # expected_make ="BMW 120D M Sport"
                # expected_year = "2008"

                    #clear data and return to home page
                    #driver.find_element(By.XPATH, "//a[@aria-label='sell my car']").click
             
                
                except Exception as e:
                    print("Element not found:", e)


        #Get data from expected output file and put into a dictrionary for assertions
                # Path to the CSV file with expected outputs
                file_path = 'C:\\Users\\rizwe\\Downloads\\car_output - V5.txt'
                
                # Load the car data into a dictionary
                car_data = load_car_data(file_path)
                
                # Query for a specific variant registration
                variant_reg = result_dict['matches'][0]
                result = get_car_details(car_data, variant_reg)
                expected_year = result.get('YEAR')
                expected_make = result.get('MAKE_MODEL')
                print(f"Details for {variant_reg}: {result}")
                    
            
                  # Assertions with clear error messages
                assert actual_year == expected_year, f"[{variant_reg}] Expected year {expected_year}, but got {actual_year}"
                assert actual_make == expected_make, f"[{variant_reg}] Expected make {expected_make}, but got {actual_make}"
        
    def teardown_method(self):
        self.driver.quit()
