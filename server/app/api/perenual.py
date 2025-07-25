import requests
import json
import logging
from config import Config

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def build_dict(arr):
    result = {}
    for item in arr:
        item_id = item.get('id', 'unknown')
        try:
            # Validate required keys
            t = item['type']
            desc = item['description']
            
            # Ensure types are correct
            if not isinstance(t, str) or not isinstance(desc, str):
                raise TypeError(f"Invalid data types for 'type' or 'description' in item with id {item.get('id')}")
            
            # Check for duplicates
            if t in result:
                raise ValueError(f"Duplicate entry for type '{t}' found in item with id {item.get('id')}")
            
            result[t] = desc
            logger.info("Added entry for type '%s' (id=%s)", t, item_id)
        
        except KeyError as ke:
            logger.error("Missing key %r in item %s", ke, item_id)
        except (TypeError, ValueError) as ve:
            logger.error("Error processing item %s: %s", item_id, ve)
        except Exception as e:
            logger.exception("Unexpected error processing item %s", item_id)
    logger.info("Finished building dict; %d entries added", len(result))
    return result

def get_care_guide(plant_name):
    url = f"{Config.PERENUAL_API}{Config.PERENUAL_ENDPOINT}?key={Config.PERENUAL_KEY}&q={plant_name}"
    response = requests.request("GET", url, headers={}, data={})
    json_data = json.loads(response.text)
    top_result = json_data["data"][0]
    care_dict = build_dict(top_result["section"])
    return care_dict