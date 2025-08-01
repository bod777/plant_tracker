from __future__ import annotations
# TO DO: Save the returning dataframe to mongodb for future use
# TO DO: Add a caching mechanism to avoid repeated API calls for the same plant
# TO DO: Check the caching mechanism for the Perenual API
# TO DO: Rework data models
# TO DO: Extract more information from the Perenual API

import logging
import json
import time
from typing import List, Dict, Tuple
from urllib.parse import urljoin, urlparse
import httpx
try:
    import pandas as pd
except ImportError:
    pd = None  # pandas is optional
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # bs4 is optional
from ..config import settings

logger = logging.getLogger(__name__)

class PerenualClient:
    """Fetches plant care data via Perenual API or scrapes the Perenual website."""

    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout
        logger.info("Initialized PerenualClient with timeout=%s", timeout)


    async def fetch_info(self, plant_name: str) -> pd.DataFrame:
        """Try API first; on 429 rate-limit, fall back to scraping."""
        logger.info("Fetching care data for plant: %s", plant_name)
        api_url = f"https://perenual.com/api/species-care-guide-list?key={settings.perenual_api_key}&q={plant_name}"
        safe_url = api_url.replace(settings.perenual_api_key or "", "<api-key>")
        logger.debug("Calling URL: %s", safe_url)

        try:
            start = time.monotonic()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(api_url)
            elapsed = time.monotonic() - start
            logger.info("Perenual API call took %.2f seconds", elapsed)

            resp.raise_for_status()
            data = resp.json()
            logger.debug("Fetched care data: %s", json.dumps(data)[:500])
            return self._parse_api_data(data)

        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            logger.error("Error fetching care guide for %s: %s", plant_name, exc)
            return pd.DataFrame(columns=self._data_columns())


    def _parse_api_data(self, data: Dict) -> pd.DataFrame:
        if 'data' not in data or not isinstance(data['data'], list):
            raise ValueError("Invalid data format: 'data' key missing or not a list")

        rows = []
        for item in data['data']:
            sci_list = item.get('scientific_name') or []
            rows.append({
                'species id': item.get('species_id'),
                'perenual scientific name': sci_list[0] if isinstance(sci_list, list) and sci_list else None,
                'perenual common name': item.get('common_name'),
                'watering': next((s.get('description') for s in item.get('section', []) if s.get('type') == 'watering'), None),
                'sunlight': next((s.get('description') for s in item.get('section', []) if s.get('type') == 'sunlight'), None),
                'pruning': next((s.get('description') for s in item.get('section', []) if s.get('type') == 'pruning'), None),
            })
        return pd.DataFrame(rows, columns=self._data_columns())


    async def _scrape_all(self, query: str) -> pd.DataFrame:
        urls = await self.scrape_search(query)
        results = []
        for url in urls:
            info = await self.scrape_page(url)
            info['search_term'] = query
            results.append(info)
        return pd.DataFrame(results, columns=self._data_columns() + ['search_term'])


    async def scrape_search(self, query: str) -> List[str]:
        logger.info("Scraping search results for: %s", query)
        search_url = "https://perenual.com/plant-species-database-search-finder"
        base = "https://perenual.com/plant-database-search-guide/species/"
        headers = {"User-Agent": "Mozilla/5.0"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(search_url, params={"search": query}, headers=headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        urls = [urljoin(base, a.get('href')) for a in soup.select('.search-container-box')]
        logger.debug("Found %d search results", len(urls))
        return urls


    async def scrape_page(self, url: str) -> Dict[str, str]:
        logger.info("Scraping care page at: %s", url)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        paras = soup.select("p.whitespace-pre-wrap")[:3]
        texts = [p.get_text(strip=True) for p in paras]
        keys = ['watering', 'sunlight', 'pruning']

        result = dict(zip(keys, texts))
        result['species id'] = urlparse(url).path.rstrip('/').split('/')[-1]
        result['perenual common name'] = soup.select_one('h1').get_text(strip=True)
        result['perenual scientific name'] = soup.select_one('h2').get_text(strip=True)
        logger.debug("Extracted care information: %s", result)
        return result


    async def get_plant_info(self, identified_plant: Dict) -> Tuple[Dict, pd.DataFrame]:
        names = [identified_plant.get("scientific_name", "")] + identified_plant.get("common_names", [])                    
        df = pd.DataFrame(columns=['search_term', 'species id', 'perenual scientific name', 'perenual common name', 'watering', 'sunlight', 'pruning'])

        logger.debug("Attempting to fetch care data for names: %s", names)
        for name in names:
            try:
                care_df = await self.fetch_info(name)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    logger.warning("Perenual API quota exceeded for %s. Falling back to scraping.", name)
                    break
            care_df['search_term'] = name
            df = pd.concat([df, care_df], ignore_index=True)
            logger.info("Number of care entries found for '%s': %d", name, len(care_df))
            logger.info("Total number of entries: %s ", len(df))

        best_match = self._get_best_match_row(df, "perenual scientific name", identified_plant.get("scientific_name", ""))
        if best_match['similarity_score'] < 0.5:
            logger.warning("No sufficiently similar match found for scientific name '%s'", identified_plant.get("scientific_name", ""))
            scraped_care_array = []
            for name in names:
                search_results = await self.scrape_search(name)
                
                for _url in search_results:
                    care_dict = await self.scrape_page(_url)
                    care_dict['search_term'] = name
                    scraped_care_array.append(care_dict)
                
            scraped_care_df = pd.DataFrame(scraped_care_array, columns=['search_term', 'species id', 'perenual scientific name', 'perenual common name', 'watering', 'sunlight', 'pruning'])
            
            best_match = self._get_best_match_row(scraped_care_df, "perenual scientific name", identified_plant.get("scientific_name", ""))
            df = pd.concat([df, scraped_care_df], ignore_index=True)

        identified_plant.update(best_match)
        logger.info("Completed identification and care retrieval")
        return identified_plant, df


    @staticmethod
    def _data_columns() -> List[str]:
        return ['species id', 'perenual scientific name', 'perenual common name', 'watering', 'sunlight', 'pruning']
