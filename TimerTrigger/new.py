import logging
import json
import requests
from datetime import datetime, timezone
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData

app = func.FunctionApp()

# App Settings (استخدم Azure Portal)
AZURE_MAPS_KEY = "MEf5Ey7DKZcevR4aa2CItXjIgnYqg5NhXHBJCrARwW6tLNlIkdKiJQQJ99BJAC5RqLJXZEq6AAAgAZMP2HQE"
EVENTHUB_CONNECTION_STR = "Endpoint=sb://trafficevents.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=KSO40tZT2YRxcgvbWASeCowhtMjb3rX7W+AEhJReg3E="
EVENTHUB_NAME = "TrafficEvents"

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
            logging.error(f"[ERROR] {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"[EXCEPTION] Failed to fetch data: {e}")
        return None


def send_to_eventhub(data, city_name):
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=EVENTHUB_CONNECTION_STR,
            eventhub_name=EVENTHUB_NAME
        )

        with producer:
            batch = producer.create_batch()
            logs = []

            if "data" in data and "features" in data["data"]:
                for feature in data["data"]["features"]:
                    props = feature.get("properties", {})
                    geom = feature.get("geometry", {})
                    coords = geom.get("coordinates", [None, None])
                    raw_timestamp = props.get("lastModifiedTime")

                    try:
                        if raw_timestamp:
                            parsed_time = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
                        else:
                            parsed_time = datetime.now(timezone.utc)
                        timestamp_iso = parsed_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    except Exception:
                        timestamp_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                    event = {
                        "city": city_name,
                        "latitude": coords[1],
                        "longitude": coords[0],
                        "description": props.get("description", "No description"),
                        "incidentType": props.get("incidentType"),
                        "severity": props.get("severity"),
                        "isRoadClosed": props.get("isRoadClosed"),
                        "delay": props.get("delay"),
                        "title": props.get("title"),
                        "timestamp": timestamp_iso
                    }

                    logging.info(json.dumps(event, ensure_ascii=False, indent=2))
                    logs.append(event)
                    batch.add(EventData(json.dumps(event, ensure_ascii=False)))

            else:
                event = {
                    "city": city_name,
                    "latitude": None,
                    "longitude": None,
                    "description": "No incidents found",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                }
                logging.info(json.dumps(event, ensure_ascii=False, indent=2))
                logs.append(event)
                batch.add(EventData(json.dumps(event, ensure_ascii=False)))

            producer.send_batch(batch)
            logging.info(f"[INFO] ✅ {city_name} data sent successfully.")

    except Exception as e:
        logging.error(f"[EXCEPTION] Failed to send to Event Hub: {e}")


# -------------------------
# Main TimerTrigger (v2 Model)
# -------------------------
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="mytimer", run_on_startup=False)
def TimerTrigger(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info(f"Timer executed at: {utc_timestamp}")

    for city in cities:
        bbox = f"{city['minLon']},{city['minLat']},{city['maxLon']},{city['maxLat']}"
        data = get_azure_maps_data(bbox)

        if data:
            send_to_eventhub(data, city["name"])
