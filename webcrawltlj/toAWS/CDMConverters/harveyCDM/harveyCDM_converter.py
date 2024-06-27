# mywebcrawler/spiders/bestdenkiCDM_converter.py

## History
# 06/03: Created converter, taken from Renee. Converts Harvey JSON files to agreed CDM
# 07/03: Added in logic for "WASHING MACHINE / DRYER" category

## Last modified: Tuesday, 7 Mar, Renee

import json
from datetime import datetime
import os
import boto3

s3 = boto3.client('s3')
bucket_name = 'raw-data-fyp'

category_dict = {'TV': 'TV', 'TVS': 'TV', 'OLED': 'TV', 'MINILED': 'TV', 'FRIDGE': 'FRIDGE', 'FRIDGES': 'FRIDGE', 'REFRIGERATOR': 'FRIDGE', 'REFRIDGERATOR': 'FRIDGE', 'FREEZER': 'FRIDGE', 'COOLER': 'FRIDGE', 'WINE CELLAR': 'FRIDGE', 'CHILLER': 'FRIDGE', 'WASHER CUM DRYER': 'WASHING MACHINE / DRYER', 'WASHING MACHINE': 'WASHING MACHINE', 'WASHER': 'WASHING MACHINE', 'WASHING MACHINES': 'WASHING MACHINE', 'FRONT LOAD WASHING MACHINE': 'WASHING MACHINE', 'TOP LOAD WASHING MACHINE': 'WASHING MACHINE', 'DRYER': 'DRYER', 'DRYERS': 'DRYER', 'FRONT LOAD': 'WASHING MACHINE / DRYER', 'FULLY AUTO': 'WASHING MACHINE / DRYER', 'FULLY-AUTO': 'WASHING MACHINE / DRYER', 'GAS COOKER': 'GAS HOB', 'STANDING COOKER': 'GAS HOB', 'GAS HOB': 'GAS HOB', 'INDUCTION COOKER': 'INDUCTION HOB', 'INDUCTION': 'INDUCTION HOB', 'INDUCTION HOB': 'INDUCTION HOB', 'BUILT-IN HOB': 'INDUCTION / GAS HOB', 'HOOD': 'HOOD', 'OVEN': 'OVEN', 'OVENS': 'OVEN', 'FAN': 'FAN', 'FANS': 'FAN', 'STAND FANS': 'FAN', 'WATER PURIFIER': 'WATER PURIFIER', 'WATER FILTERS': 'WATER PURIFIER', 'AIR CON': 'AIR CONDITIONER', 'AIRCON': 'AIR CONDITIONER', 'AIR CONDITIONER': 'AIR CONDITIONER', 'AIR CONDITIONERS': 'AIR CONDITIONER', 'AIR CONDITIONING': 'AIR CONDITIONER', 'VACUUM CLEANER': 'VACUUM CLEANER', 'VACUUM CLEANERS': 'VACUUM CLEANER', 'VACUUM': 'VACUUM CLEANER', 'RECHARGEABLE VAC': 'VACUUM CLEANER', 'AIR PURIFIER': 'AIR PURIFIER', 'AIR PURIFIERS': 'AIR PURIFIER', 'SMART LOCK': 'SMART LOCK', 'DIGITAL DOOR LOCK': 'SMART LOCK', 'FRYER': 'AIRFRYER', 'FRYERS': 'AIRFRYER', 'AIR FRYER': 'AIRFRYER', 'AIRFRYER DEEP FRYER': 'AIRFRYER', 'COFFEE MAKER MACHINE': 'COFFEE MACHINE', 'COFFEE MACHINE': 'COFFEE MACHINE', 'COFFEE MACHINES': 'COFFEE MACHINE', 'ESPRESSO MACHINE': 'COFFEE MACHINE', 'WATER HEATER': 'WATER HEATER', 'BURNER': 'GAS HOB'}

def convertCurrJson(jsonName):
    # input_filepath = os.path.join('output', 'harvey', jsonName + '.json')
    # output_filepath = os.path.join('output', 'harvey', jsonName + '_corrected.json')

    # with open(input_filepath, 'r') as file:
    #     existing_data = json.load(file)
    response = s3.get_object(Bucket=bucket_name, Key=jsonName)
    data = response['Body'].read().decode('utf-8')
    data = json.loads(data)


    def transform_entry(entry):
        
        # Lowercase all keys in the entry for easier comparison
        entry = {key.lower(): value for key, value in entry.items()}

        if 'brand' not in entry or entry['brand'] == None or entry['brand'] == "":
            name = entry['name'].split(' ')[0]
            brand = name if 'name' in entry else 'UNKNOWN'
            entry['brand'] = brand
        else:
            entry['brand'] = entry['brand'].upper()
            brand = entry['brand']

        def check_category(model, category_dict):
            model = model.upper()  # Convert to uppercase
            for keyword, category in category_dict.items():
                if keyword in model:
                    return category.upper()  # Convert to uppercase
            return 'OTHERS'

        #search for category in the model, if not found, find the category in the category dict from "model"
        if 'category' not in entry:
            category = check_category(entry['model'], category_dict)
        
        else:
            if "DRYER" in entry['model'].upper() and ("WASHING MACHINE" in entry['model'].upper() or "WASHER" in entry['model'].upper()):
                category = "WASHING MACHINE / DRYER"
            else:
                category = category_dict.get(entry['category'].upper(), 'OTHERS')

        if 'discountpercentage' not in entry: 
            try:
                entry['discountpercentage'] = (float(entry['listedprice']) - float(entry['discountedprice'])) / float(entry['listedprice']) * 100
            except ValueError:
                print("Error calculating discount percentage:", entry)

        if 'BUNDLE' in entry['model'].upper():
            category = entry['category'].upper() + ' BUNDLE'

        return {
            'platform': entry['platform'].upper(),  # Convert to uppercase
            'category': category,
            'brand': entry['brand'].upper(),  # Convert to uppercase
            'model': entry['model'].upper(),  # Convert to uppercase
            'discountedPrice': entry['discountedprice'],
            'listedPrice': entry['listedprice'],
            'discountPercentage': entry['discountpercentage'],
            'dateCollected': entry['datecollected'],
            # 'hasBundle?': False,
            # 'bundleBrand': "-",
            # 'bundleModel': "-",
            # 'bundleItem': "-",
        }

    transformed_data = [transform_entry(entry) for entry in data]
    s3.put_object(Bucket='cleaned-data-fyp', Key=jsonName, Body=json.dumps(transformed_data, indent=0))

    
       

def convert_multiple_files(file_list):
    for filename in file_list[::-1]:
        convertCurrJson(filename)

    
def list_new_files():
    new_files = []
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix='Harvey')

    for page in pages:
        for obj in page['Contents']:
            new_files.append(obj['Key'])

    # if 'Contents' in response:
    #     for obj in response['Contents']:
    #         if "Harvey" in obj['Key']:
    #             print(obj)
            
    return new_files


def main():
    files = list_new_files()

    convert_multiple_files(files[1:])
    # return list_new_files(bucket_name)

if __name__ == "__main__":
    # Call the lambda_handler function and print its return value
    response = main()