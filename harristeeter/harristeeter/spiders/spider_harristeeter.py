import scrapy
import requests
import json
import csv

class SpiderHarristeeterSpider(scrapy.Spider):
    name = "spider_harristeeter"
    BASE_URL = "https://www.harristeeter.com"
    API_URL = "https://www.harristeeter.com/atlas/v1/stores/v2/locator"

    payload = {
        'api_key': '621b20ec8d6e7d27219a388c47b42a70',
        'url': 'https://www.harristeeter.com/seo-store-files/link-hub/store-details-states/nc-grocery.json',
        'autoparse': 'true',
        'output_format': 'csv',
        'country_code': 'us',
        'device_type': 'desktop',
        'max_cost': '100'
    }

    r = requests.get('https://api.scraperapi.com/', params=payload)
    if r.status_code == 200:
        data = json.loads(r.text)
        cities = data.get('data', [])

        with open('store_details.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['City', 'City URL', 'Location ID', 'Store URL', 'Address', 'CityTown', 'Name', 'PostalCode', 'StateProvince', 'Residential', 'Latitude', 'Longitude', 'PhoneNumber'])

            for city in cities:
                city_name = city['text'].lower().replace(" ", "-")
                city_url = f"https://www.harristeeter.com/seo-store-files/link-hub/store-details-cities/{city_name}-nc-grocery.json"
                print(f"Generated City URL: {city_url}")

                payload2 = {
                    'api_key': '621b20ec8d6e7d27219a388c47b42a70',
                    'url': city_url,
                    'autoparse': 'true',
                    'output_format': 'csv',
                    'country_code': 'us',
                    'device_type': 'desktop'
                }

                city_response = requests.get('https://api.scraperapi.com/', params=payload2)
                if city_response.status_code == 200:
                    try:
                        city_data = city_response.json()
                        location_ids = city_data.get("locationIds", [])
                        if not location_ids:
                            print(f"No locations found for {city_name}. Response: {city_response.text}")
                            continue

                        # Fetch detailed store information for each location ID
                        for location_id in location_ids:
                          
                            store_details_url = f"{API_URL}?filter.locationIds={location_id}"
                            payload3 = {
                    'api_key': '621b20ec8d6e7d27219a388c47b42a70',
                    'url': store_details_url,
                    'autoparse': 'true',
                    'output_format': 'csv',
                    'country_code': 'us',
                    'device_type': 'desktop'
                }
                            store_response = requests.get('https://api.scraperapi.com/',params=payload3)
                            
                            if store_response.status_code == 200:
                                store_data = store_response.json()

                                try:
                                    store = store_data["data"]["stores"][0]
                                    address = store["locale"]["address"]["addressLines"][0]
                                    city_town = store["locale"]["address"]["cityTown"]
                                    name = store["locale"]["address"]["name"]
                                    postal_code = store["locale"]["address"]["postalCode"]
                                    state_province = store["locale"]["address"]["stateProvince"]
                                    residential = store["locale"]["address"]["residential"]
                                    latitude = store["locale"]["location"]["lat"]
                                    longitude = store["locale"]["location"]["lng"]
                                    phone_number = store["phoneNumber"]["pretty"]

                                    # Write store details to CSV
                                    store_url = f"{BASE_URL}/stores/grocery/nc/{city_name}/{location_id}"
                                    writer.writerow([city_name, city_url, location_id, store_url, address, city_town, name, postal_code, state_province, residential, latitude, longitude, phone_number])
                                    print(f"Writing to CSV: {city_name}, {city_url}, {location_id}, {store_url}, {address}, {city_town}, {name}, {postal_code}, {state_province}, {residential}, {latitude}, {longitude}, {phone_number}")
                                except KeyError as e:
                                    print(f"Missing data for location {location_id}: {e}")
                            else:
                                print(f"Failed to fetch details for location ID: {location_id}. HTTP Status Code: {store_response.status_code}")
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON for {city_name}. Response: {city_response.text}")
                else:
                    print(f"Failed to fetch city data for {city_name}. HTTP Status Code: {city_response.status_code}")
    else:
        print(f"Failed to fetch state data. HTTP Status Code: {r.status_code}")
