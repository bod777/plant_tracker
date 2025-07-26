import logging
import json
import difflib
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from .config import Config

logger = logging.getLogger(__name__)


class PlantInfoFetcher:
    """Helper for identifying plants and retrieving care information."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    async def identify_with_plantnet(
        self,
        image_bytes: bytes,
        organs: Optional[List[str]] = None,
    ) -> Dict[str, object]:
        """Identify a plant image using PlantNet."""
        data = {"organs": organs or ["leaf"]}
        files = {"images": ("image.jpg", image_bytes)}
        url = f"{Config.PLANTNET_API}{Config.PROJECT}?api-key={Config.PLANTNET_KEY}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, data=data, files=files)
            resp.raise_for_status()
            payload = resp.json()
        results = payload.get("results", [])
        if not results:
            raise ValueError("PlantNet returned no results")
        top = results[0]
        species = top.get("species", {})
        return {
            "score": top.get("score"),
            "common_names": species.get("commonNames", []),
            "scientific_name": species.get("scientificName"),
        }

    def _build_dict(self, sections: List[Dict[str, object]]) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for item in sections:
            item_id = item.get("id", "<unknown>")
            try:
                t = item["type"]
                desc = item["description"]
                if not isinstance(t, str) or not isinstance(desc, str):
                    raise TypeError("Invalid section entry types")
                if t in result:
                    raise ValueError(f"Duplicate section type '{t}'")
                result[t] = desc
            except KeyError as exc:
                logger.error("Missing key %s in section %s", exc, item_id)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Error processing section %s", item_id)
        return result

    async def fetch_care_from_perenual(self, plant_name: str) -> Dict[str, str]:
        """Query the Perenual API for care instructions."""
        url = (
            f"{Config.PERENUAL_API}{Config.PERENUAL_ENDPOINT}?key={Config.PERENUAL_KEY}&q={plant_name}"
        )
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as exc:
                logger.error("Failed fetching Perenual care guide for %s: %s", plant_name, exc)
                return {}
            except json.JSONDecodeError as exc:
                logger.error("Invalid JSON for %s: %s", plant_name, exc)
                return {}
        try:
            top = data["data"][0]
            sections = top.get("section", [])
            return self._build_dict(sections)
        except (KeyError, IndexError, TypeError) as exc:
            logger.error("Unexpected response structure for %s: %s", plant_name, exc)
            return {}

    async def scrape_perenual_search(self, query: str) -> List[Tuple[str, str]]:
        """Scrape search results from the Perenual website."""
        base = "https://perenual.com/plant-species-database-search-finder"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(base, params={"search": query}, headers=headers)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("Error searching Perenual for %s: %s", query, exc)
                return []
        soup = BeautifulSoup(resp.text, "html.parser")
        results: List[Tuple[str, str]] = []
        for a in soup.select(".search-container-box a[href]"):
            url = urljoin(base, a.get("href"))
            name = a.get_text(strip=True)
            results.append((name, url))
        return results

    async def scrape_perenual_page(self, url: str) -> Dict[str, str]:
        """Scrape a specific plant page on Perenual for care details."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                logger.error("Error fetching Perenual page %s: %s", url, exc)
                return {}
        soup = BeautifulSoup(resp.text, "html.parser")
        paras = soup.select("p.whitespace-pre-wrap")
        texts = [p.get_text(strip=True) for p in paras[:3]]
        keys = ["watering", "sunlight", "pruning"]
        return dict(zip(keys, texts))

    async def get_plant_info(self, image_path: str) -> Dict[str, object]:
        """Identify a plant image and gather care details."""
        with open(image_path, "rb") as img:
            img_bytes = img.read()

        identified = await self.identify_with_plantnet(img_bytes)
        names = [identified.get("scientific_name", "")] + identified.get("common_names", [])
        care = await self.fetch_care_from_perenual(identified["scientific_name"])
        if not care:
            for name in identified.get("common_names", []):
                care = await self.fetch_care_from_perenual(name)
                if care:
                    break
        if not care:
            search_results = await self.scrape_perenual_search(identified["scientific_name"])
            if search_results:
                ranked = self._rank_by_similarity(search_results, names)
                for _name, url in ranked:
                    care = await self.scrape_perenual_page(url)
                    if care:
                        break
        identified.update(care)
        return identified

    def _rank_by_similarity(self, results: List[Tuple[str, str]], names: List[str]) -> List[Tuple[str, str]]:
        def score(title: str) -> float:
            title_lower = title.lower()
            best = 0.0
            for n in names:
                if not n:
                    continue
                best = max(best, difflib.SequenceMatcher(None, title_lower, n.lower()).ratio())
            return best
        return sorted(results, key=lambda t: score(t[0]), reverse=True)

