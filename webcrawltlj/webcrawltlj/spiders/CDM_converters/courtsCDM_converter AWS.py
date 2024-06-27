# mywebcrawler/spiders/courtsCDM_converter.py

## History
# 06/03: Created converter for AWS, it takes in the json files from AWS S3 buckets and converts the data for courts

## Last modified: Tuesday, 6 Mar, Renee

import json
from datetime import datetime
import boto3

#change the above category_list to a dictionary
category_dict = {'TV': 'TV', 'SUBWOOFER': 'TV', 'SPEAKER': 'TV', 'MOUNT': 'TV', 'FRIDGE': 'FRIDGE', 'REFRIGERATOR': 'FRIDGE', 'REFRIDGERATOR': 'FRIDGE', 'FREEZER': 'FRIDGE', 'COOLER': 'FRIDGE', 'WINE CELLAR': 'FRIDGE', 'WINE CHILLER': 'FRIDGE', 'WASHING MACHINE': 'WASHING MACHINES', 'WASHING MACHINES': 'WASHING MACHINES', 'FRONT LOAD WASHING MACHINE': 'WASHING MACHINES', 'TOP LOAD WASHING MACHINE': 'WASHING MACHINES', 'GAS COOKER': 'GAS COOKER', 'STANDING COOKER': 'GAS COOKER', 'GAS HOB': 'GAS COOKER', 'INDUCTION COOKER': 'INDUCTION COOKER', 'INDUCTION HOB': 'INDUCTION COOKER', 'DRYER': 'DRYER', 'HOOD': 'HOOD', 'OVEN': 'OVEN', 'OVENS': 'OVEN', 'FAN': 'FAN', 'WATER PURIFIER': 'WATER PURIFIER', 'AIR CON': 'AIR CONDITIONER', 'VACUUM CLEANER': 'VACUUM CLEANER', 'AIR PURIFIER': 'AIR PURIFIER', 'SMART LOCK': 'SMART LOCK', 'DIGITAL DOOR LOCK': 'SMART LOCK', 'FRYER': 'AIRFRYER', 'AIRFRYER DEEP FRYER': 'AIRFRYER', 'COFFEE MAKER MACHINE': 'COFFEE MAKER MACHINE', 'WATER HEATER': 'WATER HEATER'}

def convert_Json(jsonName, bucket_name):
    s3 = boto3.client('s3')

    input_key = f'courts/{jsonName}.json'
    output_key = f'courts-corrected/{jsonName}_corrected.json'

    # Read JSON data from input S3 bucket
    response = s3.get_object(Bucket=input_bucket, Key=input_key)
    existing_data = json.loads(response['Body'].read().decode('utf-8'))

    def transform_entry(entry):

        # Lowercase all keys in the entry for easier comparison
        entry = {key.lower(): value for key, value in entry.items()}

        def check_category(model, category_dict):
            model = model.upper()  # Convert to uppercase
            for keyword, category in category_dict.items():
                if keyword in model:
                    entry['category'] = category.upper()  # Convert to uppercase
                    return entry['category']
                else:
                    entry['category'] = 'OTHERS'
            return entry.get('category', 'NaN')

        #search for category in the model, if not found, find the category in the category dict from "model"
        if 'category' not in entry:
            category = check_category(entry['model'], category_dict)
            entry['category'] = category
        
        else:
            entry['category'] = category_dict.get(entry['category'].upper(), 'OTHERS')            
        
        # Check for both 'date collected' and 'datecollected' keys and use the existing one
        date_collected = entry.get('date collected') or entry.get('datecollected')
        if date_collected:
            try:
                # Convert date from "dd/mm/yyyy" to "yyyy-mm-dd" format
                date_obj = datetime.strptime(date_collected, "%d/%m/%Y")
                entry['date collected'] = date_obj.strftime("%Y-%m-%d")
            except ValueError:
                print("Error converting date:", date_collected, "in entry:", entry)

        return {
            'platform': entry['platform'].upper(),  # Convert to uppercase
            'category': entry['category'].upper(),  # Convert to uppercase
            'brand': entry['brand'].upper(),  # Convert to uppercase
            'model': entry['model'].upper(),  # Convert to uppercase
            'discountedPrice': entry['discounted price'],
            'listedPrice': entry['listed price'],
            'discountPercentage': entry['discount percentage'],
            'dateCollected': entry['date collected'],
            # 'hasBundle?': False,
            # 'bundleBrand': "-",
            # 'bundleModel': "-",
            # 'bundleItem': "-",
        }

    transformed_data = [transform_entry(entry) for entry in existing_data]

    # Upload transformed JSON file to S3
    s3.put_object(
        Bucket=bucket_name,
        Key=output_key,
        Body=json.dumps(transformed_data).encode('utf-8')
    )

def convert_multiple_files(bucket_name, folder_name):
    s3 = boto3.client('s3')
    
    # List objects in the specified folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
    
    # Extract file names from the response
    files = [obj['Key'] for obj in response.get('Contents', [])]
    
    # Extract file names without extension
    file_list_without_extension = [file.split('/')[-1].split('.')[0] for file in files]
    
    # Process each file
    for filename in file_list_without_extension:
        convert_Json(filename, bucket_name)

# Provide your AWS S3 bucket name and folder name
input_bucket = 'raw-data-fyp'
output_bucket = 'converted-data-fyp'
output_folder = 'output_courts'

# Call the function to convert and upload multiple files
convert_multiple_files(input_bucket, output_bucket, output_folder)
