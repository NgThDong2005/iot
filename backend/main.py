import asyncio
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from os import environ as env
from typing import Callable

import aiofiles
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
import uvicorn

from backend.modules.auth import auth_controller
from backend.modules.dashboard import dashboard_controller
from backend.state import AppState


def homepage_handler(dev: bool) -> Callable[[Request], Awaitable[Response]]:
	if dev:

		async def handler(_: Request) -> Response:
			async with aiofiles.open("dist/index.html") as f:
				data = await f.read()

			return HTMLResponse(data)

		return handler

	with open("dist/index.html") as f:
		data = f.read()

	response = HTMLResponse(data)

	async def handler(_: Request) -> Response:
		return response

	return handler


dev = env.get("DEV") is not None
port = int(env.get("PORT", default="3000"))
host = env.get("HOST", default="0.0.0.0")


@asynccontextmanager
async def lifespan(app: Starlette):
	if dev:
		proc = await asyncio.create_subprocess_exec(
			"npm",
			"run",
			"build",
			"--",
			"--watch",
			"--sourcemap",
			"inline",
			"--minify",
			"false",
		)
		state = AppState.init(app)
		yield
		state.deinit()
		if proc.returncode is None:
			proc.terminate()
			await proc.wait()
	else:
		state = AppState.init(app)
		yield
		state.deinit()


app = Starlette(
	routes=[
		Route("/", homepage_handler(dev), methods=["GET"]),
		Mount("/assets", StaticFiles(directory="dist/assets"), name="assets"),
		Mount("/auth", routes=auth_controller.routes),
		Mount("/dashboard", routes=dashboard_controller.routes),
	],
	lifespan=lifespan,
)

if __name__ == "__main__":
	if dev:
		uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=True)
	else:
		uvicorn.run(app, host=host, port=port)
