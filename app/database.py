import asyncpg

from config import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD


class Database:

    @classmethod
    async def _action(cls, method, query):
        db = await asyncpg.create_pool(
            database=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host="postgres"
        )
        async with db.acquire() as conn:
            data =  await getattr(conn, method)(query)
        await db.close()
        return data

    @classmethod
    async def execute(cls, query):
        await cls._action("execute", query)

    @classmethod
    async def fetch(cls, query):
        return await cls._action("fetch", query)

    @classmethod
    async def save_countries(cls, countries_data):
        vals = ", ".join("(%s)" % ", ".join("'%s'" % field for field in country) for country in countries_data)
        await cls.execute(
            "INSERT INTO countries (country, region, population, world_percent, date, source, notes) VALUES %s;" % vals
        )

    @classmethod
    async def get_countries(cls):
        query = """
            SELECT region,
                region_population,
                max(min_country) AS min_country,
                min_country_population,
                max(max_country) AS max_country,
                max_country_population
            FROM
            (SELECT region,
                    region_population,
                    CASE
                        WHEN population = min_country_population THEN country
                    END AS min_country,
                    min_country_population,
                    CASE
                        WHEN population = max_country_population THEN country
                    END AS max_country,
                    max_country_population
            FROM
                (SELECT region,
                        country,
                        population,
                        sum(population) OVER (PARTITION BY region) AS region_population,
                        min(population) OVER (PARTITION BY region) AS min_country_population,
                        max(population) OVER (PARTITION BY region) AS max_country_population
                FROM countries) t
            WHERE min_country_population = population OR population = t.max_country_population) t
            GROUP BY (region,
                    region_population,
                    min_country_population,
                    max_country_population);
        """
        return await cls.fetch(query)
