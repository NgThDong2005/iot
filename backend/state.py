from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from os import environ as env

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.applications import Starlette
from starlette.requests import HTTPConnection
from starlette.websockets import WebSocket

from backend.models import Base


import paho.mqtt.client as paho
from paho.mqtt.client import Client
from paho import mqtt


MQTT_HOST = env.get("MQTT_HOST", "localhost") 
MQTT_PORT = int(env.get("MQTT_PORT", 8883))
MQTT_USER = env.get("MQTT_USER", "")
MQTT_PASS = env.get("MQTT_PASS", "")

def init_mqtt() -> Client :
	client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)

	# setting callbacks for different events to see if it works, print the message etc.
	def on_connect(client, userdata, flags, rc, properties=None):
		print("CONNACK received with code %s." %rc)
	client.on_connect = on_connect

	# with this callback you can see if your publish was successful
	def on_publish(client, userdata, mid, properties=None):
		print("mid: " + str(mid))
	client.on_publish = on_publish

	# print which topic was subscribed to
	def on_subscribe(client, userdata, mid, granted_qos, properties=None):
		print("Subscribed: " + str(mid) + " " + str(granted_qos))
	client.on_subscribe = on_subscribe
	
	# print message, useful for checking if it was successful
	def on_message(client, userdata, msg):
		print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	client.on_message = on_message

	client.tls_set( 
		tls_version=mqtt.client.ssl.PROTOCOL_TLS	
    )

	client.username_pw_set(MQTT_USER, MQTT_PASS)
	client.connect(MQTT_HOST, MQTT_PORT)
	
	client.loop_start()
	print("MQTT connected to HiveMQ Cloud!")

	return client

def start_task(
	callback: Callable[[], Awaitable[None]], interval: float
) -> asyncio.Task[None]:
	async def task():
		while True:
			await callback()
			await asyncio.sleep(interval)

	return asyncio.create_task(task())


@dataclass
class AppState:
	db_engine: Engine
	session: sessionmaker[Session]

	ws_connections: set[WebSocket]

	mqtt_client: Client = init_mqtt()

	sensor_task: asyncio.Task[None] | None = None


	@classmethod
	def init(cls, app: Starlette) -> AppState:
		db_url = env.get("DATABASE_URL", default="sqlite:///./data.db")
		connect_args = {}
		if db_url.startswith("sqlite"):
			connect_args = {"check_same_thread": False}

		engine = create_engine(db_url, connect_args=connect_args)

		Base.metadata.create_all(bind=engine)

		state = cls(
			db_engine=engine,
			session=sessionmaker(
				autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
			),
			ws_connections=set(),
		)

		app.state.data = state

		return state

	async def deinit(self) -> None:
		if self.sensor_task is not None:
			self.sensor_task.cancel()

		if self.ws_connections:
			await asyncio.gather(
				*(
					connection.close(code=1001, reason="Closing server")
					for connection in self.ws_connections
				)
			)

		self.db_engine.dispose()

	@contextmanager
	def get_db(self) -> Generator[Session]:
		db = self.session()
		try:
			yield db
			db.commit()
		except Exception:
			db.rollback()
			raise
		finally:
			db.close()

	@staticmethod
	def get(request: HTTPConnection) -> AppState:
		return request.app.state.data
	