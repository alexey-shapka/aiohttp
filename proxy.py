import asyncio

import aiohttp
from aiohttp import web


async def get_url(request):
    service_url = "http://habrahabr.ru"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(service_url + request.path) as response:
                return web.Response(status=response.status, text=await response.text(), content_type="text/html")
        except aiohttp.client_exceptions.ClientConnectorError:
            return web.Response(status=503, text="Cannot connect to %s" % service_url)


async def setup_app():
    app = web.Application()
    app.router.add_route("GET", "/{url:.*}", get_url)
    return app


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(setup_app())
    web.run_app(app)
