import asyncio
from collections.abc import Coroutine
from contextlib import asynccontextmanager
from os import environ as env
from typing import Any, Callable

import aiofiles
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
import uvicorn
import watchfiles

from backend.modules.auth import auth_controller
from backend.state import AppState


def homepage_handler(dev: bool) -> Callable[[Request], Coroutine[Any, Any, Response]]:
	if dev:

		async def handler(_: Request) -> Response:
			async with aiofiles.open("dist/index.html") as f:
				data = await f.read()

			return Response(data, media_type="text/html")

		return handler

	with open("dist/index.html") as f:
		data = f.read()

	response = Response(data, media_type="text/html")

	async def handler(_: Request) -> Response:
		return response

	return handler


dev = env.get("DEV") is not None
port = int(env.get("PORT", default="3000"))
host = env.get("HOST", default="0.0.0.0")


async def build_frontend():
	proc = await asyncio.create_subprocess_exec("npm", "run", "build")
	await proc.communicate()


async def frontend_watcher():
	async for _ in watchfiles.awatch("frontend"):
		try:
			await build_frontend()
		except asyncio.CancelledError:
			break


@asynccontextmanager
async def lifespan(app: Starlette):
	if dev:
		await build_frontend()
		task = asyncio.create_task(frontend_watcher())
		AppState.init(app)
		yield
		task.cancel()
	else:
		AppState.init(app)


app = Starlette(
	routes=[
		Route("/", homepage_handler(dev), methods=["GET"]),
		Mount("/assets", StaticFiles(directory="dist/assets"), name="assets"),
		Mount("/auth", routes=auth_controller.routes),
	],
	lifespan=lifespan,
)

if __name__ == "__main__":
	if dev:
		uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=True)
	else:
		uvicorn.run(app, host=host, port=port)
