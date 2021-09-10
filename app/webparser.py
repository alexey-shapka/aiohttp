import re

import aiohttp
from bs4 import BeautifulSoup

from config import WEB_SOURCE


class WebParser:

    urls = {
        "wiki": "https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population",
        "stats": "https://statisticstimes.com/demographics/countries-by-population.php"
    }

    @classmethod
    async def fetch(cls, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()

    @classmethod
    async def parse_data(cls):
        parser = BeautifulSoup(await cls.fetch(cls.urls[WEB_SOURCE]), features="html.parser")
        if WEB_SOURCE == "wiki":
            return await cls.parse_wiki_data(parser)
        elif WEB_SOURCE == "stats":
            return await cls.parse_stats_data(parser)

    @classmethod
    async def parse_stats_data(cls, parser):
        table = parser.find("table", attrs={"id": "table_id"})
        countries_data = []
        for row in table.find("tbody").findAll("tr"):
            country_data = [f.getText().strip().replace("'", "\"") for f in row.findAll("td")]
            country, _, _, population, _, percent, _, _, _, region = country_data
            countries_data.append((
                country, region, population.replace(",", ""), percent, "2021", "", ""
            ))
        return countries_data

    @classmethod
    async def parse_wiki_data(cls, parser):
        table = parser.find("table", attrs={"class": "wikitable sortable"})
        countries_data = []
        for row in table.find("tbody").findAll("tr")[2:]:
            country_data = [f.getText().replace(u"\xa0", " ").strip().replace("'", "\"") for f in row.findAll("td")]
            country, region, population, percent, date, source, *notes = country_data
            countries_data.append((
                re.sub(r"\s+\(more\)", "", country), region, population.replace(",", ""), percent.rstrip("%"),
                date, re.sub(r"\[\d+]", "", source), next(iter(notes), "")
            ))
        return countries_data
