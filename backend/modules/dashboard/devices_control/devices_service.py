from backend.state import AppState


def set_relay(state: AppState, on_relay: bool) -> None:
	state.mqtt_client.publish("relay", on_relay)


def set_buzzer(state: AppState, on_buzzer: bool) -> None:
	state.mqtt_client.publish("buzzer", on_buzzer)


def set_led_color(state: AppState, led_color: str) -> None:
	state.mqtt_client.publish("led", led_color)
