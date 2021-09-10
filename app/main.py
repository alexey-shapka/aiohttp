import asyncio

from asyncpg import exceptions
from aiohttp import web
from tabulate import tabulate

from database import Database
from webparser import WebParser


async def get_data(_):
    data = await WebParser.parse_data()
    try:
        await Database.save_countries(data)
        return web.Response(text="Countries data has been parsed and saved successfully!")
    except exceptions.UniqueViolationError as e:
        return web.Response(status=400, text="Failed to save data in database:\n{}".format(str(e).strip()))


async def print_data(_):
    data = await Database.get_countries()
    try:
        table = tabulate([list(row) for row in data], headers=data[0].keys())
        return web.Response(text=table)
    except IndexError:
        return web.Response(status=404, text="Countries not found")


async def setup_app():
    app = web.Application()
    app.router.add_route("GET", "/get_data", get_data)
    app.router.add_route("GET", "/print_data", print_data)
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(setup_app())
    web.run_app(app)
