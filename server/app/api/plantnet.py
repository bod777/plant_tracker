import requests
import json
from config import Config

def prepare_data(request):
    files = []
    for image in request.image_data:
        files.append(('images', (image)))
    
    data = { 'organs': request.organs }
    
    return data, files


def identify_plant(request):
    api_endpoint = f"{Config.PLANTNET_API}{Config.PROJECT}?api-key={Config.PLANTNET_KEY}"
    
    organs, images = prepare_data(request)
    req = requests.Request('POST', url=api_endpoint, files=images, data=organs)
    prepared = req.prepare()

    s = requests.Session()
    response = s.send(prepared)
    json_result = json.loads(response.text)
    results = json_result["results"]

    score = results[0]["score"]
    common_names = results[0]["species"]["commonNames"]
    scientific_name = results[0]["species"]["scientificName"]

    return {"score": score, "common_names": common_names, "scientific_name": scientific_name}

