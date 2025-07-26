import logging
import time
import httpx
from typing import List, Dict

from config import Config
from logging_setup import redact_sensitive

logger = logging.getLogger(__name__)

class PlantNetClient:
    """Handles identification via the PlantNet API."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        logger.info("Initialized PlantNetClient with timeout=%s", timeout)

    async def identify(self, image_files: List[str], organs: List[str]) -> Dict[str, object]:
        logger.info("Identifying plant and retrieving care information")
        files = []
        for image_file in image_files:
            logger.debug("Reading image file: %s", image_file)
            image_data = open(image_file, 'rb')
            files.append(('images', image_data))

        if organs is None:
            organs = ["auto" for _ in image_files]
        logger.debug("Using organs list: %s", organs)

        data = {'organs': organs}
        logger.info("Sending identification request with data: %s", data)

        api_url = f"{Config.PLANTNET_API}{Config.PROJECT}?api-key={Config.PLANTNET_KEY}"
        safe_url = redact_sensitive(api_url)
        logger.debug("Sending image data to PlantNet API at %s", safe_url)

        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(api_url, data={"organs": organs}, files=files)
            elapsed = time.monotonic() - start
            logger.info("PlantNet API call took %.2f seconds", elapsed)

            response.raise_for_status()
            payload = response.json()
            results = payload.get("results", [])
            if not results:
                logger.warning("No results from PlantNet API")
                raise ValueError("No results returned from PlantNet API")

            top = results[0]
            species = top.get("species", {})
            return {
                "score": top.get("score"),
                "common_names": species.get("commonNames", []),
                "scientific_name": species.get("scientificName"),
            }

        except httpx.RequestError:
            logger.exception("Request to PlantNet API failed")
            raise
        except (KeyError, ValueError, TypeError) as e:
            logger.error("Error parsing PlantNet response: %s", e)
            raise