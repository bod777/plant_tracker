import os
import base64
import requests

# 1) Load your key from the environment
API_KEY = "PGWB5whk4cFI6aNSglS7IYsod7uBN1xdDLWUF3cnTtFdkATbme"

# 2) Read an image file and encode it
with open("test_photo.jpg", "rb") as f:
    img_bytes = f.read()
b64 = base64.b64encode(img_bytes).decode()

# 3) Call the Plant.id identify endpoint
resp = requests.post(
    "https://api.plant.id/v2/identify",
    headers={"Api-Key": API_KEY, "Content-Type": "application/json"},
    json={
        "images": [b64],
        "organs": ["leaf"]
    }
)

print("Status code:", resp.status_code)
print("Response JSON:", resp.json())
