# mywebcrawler/spiders/parisilkCDM_converter.py

## History
# 12/02: Created converter, it takes in the full json name and converts the columns into the CDM agreed upon
# 06/03: Modified the converter to conform to the agreed upon CDM, usign the category dictionary to map the categories more flexibly
# 07/03: Modified to populate bundleBrand data as well from brand data and added in logic for "WASHING MACHINE / DRYER" category
# 08/03: Updated category_dict to include more categories
# 09/03: Fixed check_category function 

## Last modified: Tuesday, 09 Mar, Renee

import json
from datetime import datetime
import os

def convertCurrJson(jsonName):
    input_filepath = os.path.join('output', 'parisilk', jsonName + '.json')
    output_filepath = os.path.join('output', 'parisilk', jsonName + '_corrected.json')

    with open(input_filepath, 'r') as file:
        existing_data = json.load(file)

    def transform_entry(entry):

        # Lowercase all keys in the entry for easier comparison
        entry = {key.lower(): value for key, value in entry.items()}

        model = entry['brand'].upper() + " " + entry['item'].upper() + " " + entry['model'].upper()

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
            if "DRYER" in model and ("WASHING MACHINE" in model or "WASHER" in model):
                category = "WASHING MACHINE / DRYER"
            else:
                category = category_dict.get(entry['category'].upper(), 'OTHERS')

        entry['discountedprice'] = entry['listedprice']

        if 'discountpercentage' not in entry: 
            try:
                entry['discountpercentage'] = (float(entry['listedprice']) - float(entry['discountedprice'])) / float(entry['listedprice']) * 100
            except ValueError:
                print("Error calculating discount percentage:", entry)
        
        if entry['hasbundle?'] == True:
            category_bundle = entry['category'].upper() + ' BUNDLE'
            return {
                'platform': entry['platform'].upper(),  # Convert to uppercase
                'category': category_bundle,
                'brand': entry['brand'].upper(),  # Convert to uppercase
                'model': model,
                'hasBundle?': True,
                'bundle_discountedPrice': entry['discountedprice'],
                'bundle_listedPrice': entry['listedprice'],
                'bundle_discountPercentage': entry['discountpercentage'], 
                'bundleBrand': entry['brand'].upper(),
                'bundleModel': entry['bundlemodel'].upper(),
                'bundleItem': entry['bundleitem'].upper(),
                'dateCollected': entry['datecollected'],
            }
        else:
            return {
                'platform': entry['platform'].upper(),  # Convert to uppercase
                'category': category,
                'brand': entry['brand'].upper(),  # Convert to uppercase
                'model': model,
                'discountedPrice': entry['discountedprice'],
                'listedPrice': entry['listedprice'],
                'discountPercentage': entry['discountpercentage'],
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
    
# Get the list of files in the "output/parisilk" directory
directory = os.path.join('output', 'parisilk')
file_list = os.listdir(directory)

# Filter out only the JSON files
file_list = [filename for filename in file_list if filename.endswith('.json')]

# Remove the ".json" extension from the filenames
file_list_without_extension = [filename[:-5] for filename in file_list]

category_dict = {'TV': 'TV', 'TVS': 'TV', 'OLED': 'TV', 'MINILED': 'TV', 'FRIDGE': 'FRIDGE', 'FRIDGES': 'FRIDGE', 'REFRIGERATOR': 'FRIDGE', 'REFRIDGERATOR': 'FRIDGE', 'FREEZER': 'FRIDGE', 'COOLER': 'FRIDGE', 'WINE CELLAR': 'FRIDGE', 'CHILLER': 'FRIDGE', 'WASHER CUM DRYER': 'WASHING MACHINE / DRYER', 'WASHING MACHINE': 'WASHING MACHINE', 'WASHER': 'WASHING MACHINE', 'WASHING MACHINES': 'WASHING MACHINE', 'FRONT LOAD WASHING MACHINE': 'WASHING MACHINE', 'TOP LOAD WASHING MACHINE': 'WASHING MACHINE', 'DRYER': 'DRYER', 'DRYERS': 'DRYER', 'FRONT LOAD': 'WASHING MACHINE / DRYER', 'FULLY AUTO': 'WASHING MACHINE / DRYER', 'FULLY-AUTO': 'WASHING MACHINE / DRYER', 'GAS COOKER': 'GAS HOB', 'STANDING COOKER': 'GAS HOB', 'GAS HOB': 'GAS HOB', 'INDUCTION COOKER': 'INDUCTION HOB', 'INDUCTION': 'INDUCTION HOB', 'INDUCTION HOB': 'INDUCTION HOB', 'BUILT-IN HOB': 'INDUCTION / GAS HOB', 'HOOD': 'HOOD', 'OVEN': 'OVEN', 'OVENS': 'OVEN', 'FAN': 'FAN', 'FANS': 'FAN', 'STAND FANS': 'FAN', 'WATER PURIFIER': 'WATER PURIFIER', 'WATER FILTERS': 'WATER PURIFIER', 'AIR CON': 'AIR CONDITIONER', 'AIRCON': 'AIR CONDITIONER', 'AIR CONDITIONER': 'AIR CONDITIONER', 'AIR CONDITIONERS': 'AIR CONDITIONER', 'AIR CONDITIONING': 'AIR CONDITIONER', 'VACUUM CLEANER': 'VACUUM CLEANER', 'VACUUM CLEANERS': 'VACUUM CLEANER', 'VACUUM': 'VACUUM CLEANER', 'RECHARGEABLE VAC': 'VACUUM CLEANER', 'AIR PURIFIER': 'AIR PURIFIER', 'AIR PURIFIERS': 'AIR PURIFIER', 'SMART LOCK': 'SMART LOCK', 'DIGITAL DOOR LOCK': 'SMART LOCK', 'FRYER': 'AIRFRYER', 'FRYERS': 'AIRFRYER', 'AIR FRYER': 'AIRFRYER', 'AIRFRYER DEEP FRYER': 'AIRFRYER', 'COFFEE MAKER MACHINE': 'COFFEE MACHINE', 'COFFEE MACHINE': 'COFFEE MACHINE', 'COFFEE MACHINES': 'COFFEE MACHINE', 'ESPRESSO MACHINE': 'COFFEE MACHINE', 'WATER HEATER': 'WATER HEATER', 'BURNER': 'GAS COOKER'}

# Call the function to convert multiple files
convert_multiple_files(file_list_without_extension)