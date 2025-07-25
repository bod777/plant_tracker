import dotenv
import os
dotenv.load_dotenv()

class Config:
    PERENUAL_API = "https://perenual.com/api/"
    PERENUAL_ENDPOINT = "species-care-guide-list"
    PERENUAL_KEY = os.getenv("PERENUAL_API_KEY")
    
    PLANTNET_API = "https://my-api.plantnet.org/v2/identify/"
    PLANTNET_KEY = os.getenv("PLANTNET_API_KEY")
    PROJECT = "all"