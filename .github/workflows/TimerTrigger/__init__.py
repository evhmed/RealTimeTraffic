import os
import requests
import json
from azure.eventhub import EventHubProducerClient, EventData
from datetime import datetime, UTC
from dotenv import load_dotenv

load_dotenv()
AZURE_MAPS_KEY = os.getenv("AZURE_MAPS_KEY")
EVENTHUB_CONNECTION_STR = os.getenv("EVENTHUB_CONNECTION_STR")
EVENTHUB_NAME = os.getenv("EVENTHUB_NAME")

MAPS_URL = "https://atlas.microsoft.com/traffic/incident"
MAPS_PARAMS = {
    "subscription-key": AZURE_MAPS_KEY,
    "api-version": "2025-01-01"
}

cities = [
    {"name": "Cairo", "minLon": 31.20, "minLat": 30.00, "maxLon": 31.35, "maxLat": 30.15},
    {"name": "Giza", "minLon": 31.15, "minLat": 29.95, "maxLon": 31.30, "maxLat": 30.10},
    {"name": "Alexandria", "minLon": 29.85, "minLat": 31.15, "maxLon": 30.10, "maxLat": 31.30},
    {"name": "Port Said", "minLon": 32.25, "minLat": 31.25, "maxLon": 32.35, "maxLat": 31.30},
    {"name": "Suez", "minLon": 32.30, "minLat": 29.90, "maxLon": 32.35, "maxLat": 29.95},
    {"name": "Ismailia", "minLon": 32.25, "minLat": 30.55, "maxLon": 32.35, "maxLat": 30.65}
]

def get_azure_maps_data(bbox):
    MAPS_PARAMS["bbox"] = bbox
    try:
        response = requests.get(MAPS_URL, params=MAPS_PARAMS, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[ERROR] {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[EXCEPTION] Failed to fetch data: {e}")
        return None

def send_to_eventhub(data):
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=EVENTHUB_CONNECTION_STR,
            eventhub_name=EVENTHUB_NAME
        )

        with producer:
            batch = producer.create_batch()

            if "data" in data and "incidents" in data["data"]:
                for incident in data["data"]["incidents"]:
                    coords = incident.get("geometry", {}).get("coordinates", [None, None])
                    raw_timestamp = incident.get("properties", {}).get("lastModified", "")

                    try:
                        if raw_timestamp:
                            parsed_time = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
                        else:
                            parsed_time = datetime.now(UTC)
                        timestamp_iso = parsed_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    except Exception:
                        timestamp_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                    event = {
                        "city": data.get("city", "Unknown"),
                        "latitude": coords[1],
                        "longitude": coords[0],
                        "description": incident.get("properties", {}).get("description", "No description"),
                        "timestamp": timestamp_iso
                    }

                    batch.add(EventData(json.dumps(event)))

            else:
                event = {
                    "city": data.get("city", "Unknown"),
                    "latitude": None,
                    "longitude": None,
                    "description": "No incidents found",
                    "timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
                batch.add(EventData(json.dumps(event)))

            producer.send_batch(batch)
        print(f"[INFO] {data.get('city', 'Unknown')} data sent to Event Hub successfully.")

    except Exception as e:
        print(f"[EXCEPTION] Failed to send to Event Hub: {e}")


if __name__ == "__main__":
    for city in cities:
        bbox = f"{city['minLon']},{city['minLat']},{city['maxLon']},{city['maxLat']}"
        data = get_azure_maps_data(bbox)
        if data:
            send_to_eventhub({"city": city["name"], "data": data})
