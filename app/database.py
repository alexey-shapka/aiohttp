import asyncpg


class Database:

    @classmethod
    async def _action(cls, method, query):
        db = await asyncpg.create_pool(database="countries", user="user", password="password", host="postgres")
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
            SELECT t1.region,
                t1.rp AS region_population,
                t2.maxc AS max_country,
                t2.maxp AS max_population,
                t2.minc AS min_country,
                t2.minp AS min_population
            FROM
            (SELECT region,
                    sum(population) AS rp
            FROM countries
            GROUP BY region) t1
            JOIN
            (SELECT t1.region,
                    t2.maxc,
                    t2.maxp,
                    t1.minc,
                    t1.minp
            FROM
                (SELECT region,
                        country AS minc,
                        population AS minp
                FROM countries a
                WHERE population =
                    (SELECT min(population)
                    FROM countries b
                    WHERE b.region = a.region)) t1
            JOIN
                (SELECT region,
                        country AS maxc,
                        population AS maxp
                FROM countries c
                WHERE population =
                    (SELECT max(population)
                    FROM countries d
                    WHERE d.region = c.region)) t2 ON (t1.region = t2.region)) t2 ON (t1.region = t2.region);
        """
        return await cls.fetch(query)
