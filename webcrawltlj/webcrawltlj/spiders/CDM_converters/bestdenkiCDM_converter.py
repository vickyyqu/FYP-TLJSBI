# mywebcrawler/spiders/bestdenkiCDM_converter.py

## History
# 05/03: Created converter, it takes in the full json name and converts the columns into the CDM agreed upon
# 06/03: Modified the converter to conform to the agreed upon CDM, usign the category dictionary to map the categories more flexibly
# 07/03: Modified the discount percentage calculation to handle cases where the discounted price is greater than the listed price. Have to look into why there is discrepancy, could be Best Denki DOM change
# 08/03: Updated category_dict to include more categories
# 09/03: Fixed check_category function 

## Last modified: Tuesday, 09 Mar, Renee

import json
from datetime import datetime
import os

def convertCurrJson(jsonName):
    input_filepath = os.path.join('output', 'bestdenki', jsonName + '.json')
    output_filepath = os.path.join('output', 'bestdenki', jsonName + '_corrected.json')

    with open(input_filepath, 'r') as file:
        existing_data = json.load(file)

    def transform_entry(entry):
        
        # Lowercase all keys in the entry for easier comparison
        entry = {key.lower(): value for key, value in entry.items()}
        
        #if model is in entry but null, use the name only
        if 'model' not in entry or entry['model'] == None:
            model = entry['name'].upper()
        else:
            model = entry['name'].upper() + " " + entry['model'].upper()

        if 'brand' not in entry or entry['brand'] == None or entry['brand'] == "":
            name = entry['name'].split(' ')[0]
            brand = name if 'name' in entry else 'UNKNOWN'
            entry['brand'] = brand
        else:
            entry['brand'] = entry['brand'].upper()

        def check_category(model, category_dict):
            model = model.upper()  # Convert to uppercase
            for keyword, category in category_dict.items():
                if keyword in model:
                    return category.upper()  # Convert to uppercase
            return 'OTHERS'

        #search for category in the model, if not found, find the category in the category dict from "model"
        if 'category' not in entry:
            category = check_category(model, category_dict)
        
        else:
            if "DRYER" in entry['model'].upper() and ("WASHING MACHINE" in entry['model'].upper() or "WASHER" in entry['model'].upper()):
                category = "WASHING MACHINE / DRYER"
            else:
                category = category_dict.get(entry['category'].upper(), 'OTHERS')

        if 'discountpercentage' not in entry: 
            try:
                if entry['discountedprice'] < entry['listedprice']:
                    discount_percentage = (float(entry['listedprice']) - float(entry['discountedprice'])) / float(entry['listedprice']) * 100
                else:
                    discount_percentage = (float(entry['discountedprice']) - float(entry['listedprice'])) / float(entry['discountedprice']) * 100
            except ValueError:
                print("Error calculating discount percentage:", entry)

        if 'PACKAGE' in model:
            category = entry['category'].upper() + ' BUNDLE'
           
        return {
            'platform': entry['platform'].upper(),  # Convert to uppercase
            'category': category,
            'brand': entry['brand'].upper(),  # Convert to uppercase
            'model': model,
            'discountedPrice': entry['discountedprice'],
            'listedPrice': entry['listedprice'],
            'discountPercentage': discount_percentage,
            'dateCollected': entry['datecollected'],
            # 'hasBundle?': False,
            # 'bundleBrand': "-",
            # 'bundleModel': "-",
            # 'bundleItem': "-",
        }

    transformed_data = [transform_entry(entry) for entry in existing_data]

    with open(output_filepath, 'w') as file:
        json.dump(transformed_data, file, indent=0)

def convert_multiple_files(file_list):
    for filename in file_list:
        convertCurrJson(filename)
    
# Get the list of files in the "output/bestdenki" directory
directory = os.path.join('output', 'bestdenki')
file_list = os.listdir(directory)

# Filter out only the JSON files
# file_list = [filename for filename in file_list if filename.endswith('.json')]
#exclude json files with "links" in the name and is a json file
file_list = [filename for filename in file_list if filename.endswith('.json') and"links" not in filename]

# Remove the ".json" extension from the filenames
file_list_without_extension = [filename[:-5] for filename in file_list]

category_dict = {'TV': 'TV', 'TVS': 'TV', 'OLED': 'TV', 'MINILED': 'TV', 'FRIDGE': 'FRIDGE', 'FRIDGES': 'FRIDGE', 'REFRIGERATOR': 'FRIDGE', 'REFRIDGERATOR': 'FRIDGE', 'FREEZER': 'FRIDGE', 'COOLER': 'FRIDGE', 'WINE CELLAR': 'FRIDGE', 'CHILLER': 'FRIDGE', 'WASHER CUM DRYER': 'WASHING MACHINE / DRYER', 'WASHING MACHINE': 'WASHING MACHINE', 'WASHER': 'WASHING MACHINE', 'WASHING MACHINES': 'WASHING MACHINE', 'FRONT LOAD WASHING MACHINE': 'WASHING MACHINE', 'TOP LOAD WASHING MACHINE': 'WASHING MACHINE', 'DRYER': 'DRYER', 'DRYERS': 'DRYER', 'FRONT LOAD': 'WASHING MACHINE / DRYER', 'FULLY AUTO': 'WASHING MACHINE / DRYER', 'FULLY-AUTO': 'WASHING MACHINE / DRYER', 'GAS COOKER': 'GAS HOB', 'STANDING COOKER': 'GAS HOB', 'GAS HOB': 'GAS HOB', 'INDUCTION COOKER': 'INDUCTION HOB', 'INDUCTION': 'INDUCTION HOB', 'INDUCTION HOB': 'INDUCTION HOB', 'BUILT-IN HOB': 'INDUCTION / GAS HOB', 'HOOD': 'HOOD', 'OVEN': 'OVEN', 'OVENS': 'OVEN', 'FAN': 'FAN', 'FANS': 'FAN', 'STAND FANS': 'FAN', 'WATER PURIFIER': 'WATER PURIFIER', 'WATER FILTERS': 'WATER PURIFIER', 'AIR CON': 'AIR CONDITIONER', 'AIRCON': 'AIR CONDITIONER', 'AIR CONDITIONER': 'AIR CONDITIONER', 'AIR CONDITIONERS': 'AIR CONDITIONER', 'AIR CONDITIONING': 'AIR CONDITIONER', 'VACUUM CLEANER': 'VACUUM CLEANER', 'VACUUM CLEANERS': 'VACUUM CLEANER', 'VACUUM': 'VACUUM CLEANER', 'RECHARGEABLE VAC': 'VACUUM CLEANER', 'AIR PURIFIER': 'AIR PURIFIER', 'AIR PURIFIERS': 'AIR PURIFIER', 'SMART LOCK': 'SMART LOCK', 'DIGITAL DOOR LOCK': 'SMART LOCK', 'FRYER': 'AIRFRYER', 'FRYERS': 'AIRFRYER', 'AIR FRYER': 'AIRFRYER', 'AIRFRYER DEEP FRYER': 'AIRFRYER', 'COFFEE MAKER MACHINE': 'COFFEE MACHINE', 'COFFEE MACHINE': 'COFFEE MACHINE', 'COFFEE MACHINES': 'COFFEE MACHINE', 'ESPRESSO MACHINE': 'COFFEE MACHINE', 'WATER HEATER': 'WATER HEATER', 'BURNER': 'GAS COOKER'}

# Call the function to convert multiple files
convert_multiple_files(file_list_without_extension)