# MainApp/views.py
import os
import json
import asyncio
from datetime import date

import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from .models import Candle

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            timeframe = form.cleaned_data['timeframe']
            # print(file)
            # print(timeframe)
            # Save the file to a specific location on the server
            file_path = handle_uploaded_file(file)

            # Read the CSV file using pandas
            candles_data = read_csv_to_candles(file_path)
            # print(candles_data)
            # Perform the conversion asynchronously
            converted_candles = asyncio.run(convert_and_save_candles(candles_data, timeframe))

            # Provide the user with the option to download the JSON file
            response = download_json_file(converted_candles)

            return response

    else:
        form = UploadFileForm()

    return render(request, 'upload_file.html', {'form': form})

def handle_uploaded_file(file):
    # Define the directory where you want to save the files
    upload_dir = 'Upload'

    # Ensure the directory exists, create it if not
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Construct the file path
    file_path = os.path.join(upload_dir, file.name)

    # Save the file to the specified path
    with open(file_path, 'wb') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    return file_path

def read_csv_to_candles(file_path):
    # Read the CSV file using pandas
    df = pd.read_csv(file_path, low_memory=False)
    # print(df.head) # It prints first five rows
    # Convert DataFrame to list of dictionaries
    data_list = df.to_dict(orient='records')
    # print(data_list)
    # Convert the list of dictionaries to a list of Candle objects
    # candles_list = [Candle(
    #     open=data['OPEN'],
    #     high=data['HIGH'],
    #     low=data['LOW'],
    #     close=data['CLOSE'],
    #     date=pd.to_datetime(data['DATE']).date()
    # ) for data in data_list]
    # candle_data = {
    #     'open': data.get('OPEN'),
    #     'high': data.get('HIGH'),
    #     'low': data.get('LOW'),
    #     'close': data.get('CLOSE'),
    #     'date': pd.to_datetime(data.get('DATE')).date() if data.get('DATE') else None,
    # }
    #
    # candle = Candle(**candle_data)
    # candles_list.append(candle)
    candles_list = []
    for data in data_list:
        # print(data)  # Print the data to inspect
        candle_data = {
            'open': data.get('OPEN'),
            'high': data.get('HIGH'),
            'low': data.get('LOW'),
            'close': data.get('CLOSE'),
            'date': pd.to_datetime(data.get('DATE'), errors='coerce').date(),
        }

        # Check for missing or incorrect data
        if any(value is None for value in candle_data.values()):
            print(f"Skipping invalid data: {candle_data}")
            continue
        candle = Candle(**candle_data)
        # print(candle)
        candles_list.append(candle)
        # print(candle)  # Print the created Candle object
        # candles_list.append(candle)

    return candles_list

async def convert_and_save_candles(candles_data, timeframe):
    # Perform the conversion asynchronously
    converted_candles = await asyncio.gather(*[convert_candles(candle, timeframe) for candle in candles_data])

    # Save the converted candles to a JSON file
    json_file_path = save_candles_to_json(converted_candles)

    return json_file_path

async def convert_candles(candle, timeframe):

    converted_candle = {
        'open': candle.open,
        'high': candle.high,
        'low': candle.low,
        'close': candle.close,
        'date': candle.date
    }

    return converted_candle


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def save_candles_to_json(converted_candles):
    # Save the converted Candle objects to a JSON file
    json_data = json.dumps(converted_candles, indent=2, cls=CustomJSONEncoder)
    # print(json_data)
    # Define the directory where you want to save the JSON files
    json_dir = 'JSON_DIR'

    # Ensure the directory exists, create it if not
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)

    # Construct the JSON file path
    json_file_path = os.path.join(json_dir, 'converted_data.json')

    # Save the JSON data to the file
    with open(json_file_path, 'w') as json_file:
        json_file.write(json_data)

    return json_file_path

def download_json_file(json_file_path):
    # Provide the user with the option to download the JSON file
    with open(json_file_path, 'rb') as json_file:
        response = HttpResponse(json_file.read(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename={os.path.basename(json_file_path)}'
        return response
