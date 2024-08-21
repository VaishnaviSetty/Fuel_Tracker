import json
import os
from datetime import datetime
import pandas as pd
import requests
import schedule
import time
from config import get as config_get
from logger import logger

# URL for Diesel Prices
url_template = "https://www.livemint.com/api/cms/fuelprice/gethistoricaldata/city/diesel/{}/365"

def get_data_for_city(city: str):
    """
    Get fuel data for the given city
    """
    logger.info(f"Trying to fetch data for city: {city}")

    try:
        url = url_template.format(city.replace(" ", "-").lower())
        response = requests.get(url)
        logger.info(f"Response code: {response.status_code}")

        if response.status_code != 200:
            raise Exception(f"HTTP Response Code: {response.status_code}")

        data = response.json()
        df = pd.json_normalize(data)
        df['City Name'] = city
        df['Date'] = pd.to_datetime(df['date'])
        df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')
        df['Month'] = pd.to_datetime(df['date']).dt.strftime('%B-%Y')
        df = df[['City Name', 'price', 'Date', 'Month']]
        df.rename(columns={'price': 'Price'}, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df.sort_values(by=['Date'], inplace=True)
        df.reset_index(drop=True, inplace=True)
        logger.info(f"Got data for {city}. Records: {df.shape[0]}")
        return df
    except Exception as e:
        logger.exception(f"Error fetching data for city: {city}. Error: {e}")
        return None

def get_fuel_data():
    cities = config_get("CITIES")
    logger.info(f"Getting data for the following cities: {cities}")
    all_data = []
    for city in cities:
        df = get_data_for_city(city)
        if df is not None:
            all_data.append(df)
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.sort_values(by=['City Name', 'Date'], inplace=True)
        combined_data.reset_index(drop=True, inplace=True)
        logger.info("Fetched and sorted data for all cities")
        return combined_data
    else:
        logger.info("No data fetched for any city")
        return pd.DataFrame()

def fetch_and_save_fuel_prices():
    data_dir = config_get("DATA_DIR")
    if not os.path.exists(data_dir):
        logger.info(f"Data directory {data_dir} doesn't exist. Creating")
        os.makedirs(data_dir)

    file_name = get_daily_file_path()

    try:
        new_data = get_fuel_data()
        
        if new_data.empty:
            logger.info("No new data fetched.")
            return
        
        # If the file exists, load it and append the new data
        if os.path.exists(file_name):
            existing_data = pd.read_excel(file_name)
            existing_data['Date'] = pd.to_datetime(existing_data['Date'], format='%d/%m/%Y')
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
            combined_data = combined_data.drop_duplicates(subset=['City Name', 'Date'], keep='last')
        else:
            combined_data = new_data
        
        # Save updated data to file
        combined_data.to_excel(file_name, index=False)
        logger.info(f"File saved as: {file_name}")

    except Exception as e:
        logger.exception(f"Something went wrong. Error: {e}")

def get_daily_file_path():
    today = datetime.now().strftime('%Y-%m-%d')
    return os.path.join(config_get("DATA_DIR"), f"daily_fuel_prices_{today}.xlsx")

def job():
    logger.info("Job started")
    fetch_and_save_fuel_prices()
    logger.info("Job completed")

# Schedule the job every day at midnight
schedule.every().day.at("00:00").do(job)

if __name__ == "__main__":
    print("Script started")
    job()  # Run job immediately for testing
    while True:
        schedule.run_pending()
        time.sleep(60)  # Wait a minute before checking again
