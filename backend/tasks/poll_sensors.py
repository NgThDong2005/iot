from backend.state import AppState


async def poll_sensors(state: AppState) -> None:
	"""
	Poll sensors and store the data in the database.
	This function is called periodically by the sensor task.
	"""
	state.mqtt_client.publish("sensor/request", "ON")
