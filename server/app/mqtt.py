import json
import logging
import os
import paho.mqtt.client as paho
import threading

from typing import Any


class Client(threading.Thread):
    def __init__(self):
        super().__init__(name='MQTT')

        self._host = os.getenv('MQTT_HOST')
        self._port = int(os.getenv('MQTT_PORT', '1883'))
        self._user = os.getenv('MQTT_USER')
        self._pass = os.getenv('MQTT_PASS')
        self._prefix = os.getenv('MQTT_PREFIX', 'face-recognition')

        self._logger = logging.getLogger(__name__)
        self._client = paho.Client(client_id='face-recognition')

        if self._user:
            self._client.username_pw_set(self._user, self._pass)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc):
        """
        On connect event
        """
        if rc == 0:
            self._logger.info('Connected successfully to MQTT broker')
        else:
            self._logger.warning('Unable to connect to MQTT broker: %d', rc)

    def _on_disconnect(self, client, userdata, rc):
        """
        On disconnect event
        """
        if rc == 0:
            self._logger.info('Disconnected from mqtt://%s:%d', self._host, self._port)

    def start(self) -> None:
        self._logger.debug('Connecting to mqtt://%s:%d', self._host, self._port)
        self._client.connect(self._host, self._port)
        super().start()

    def run(self) -> None:
        self._client.loop_forever()

    def stop(self):
        self._logger.debug('Disconnecting from mqtt://%s:%d', self._host, self._port)
        self._client.disconnect()

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False):
        topic = f'{self._prefix}/{topic}' if self._prefix else topic
        return self._client.publish(topic, json.dumps(payload), qos, retain)

client = Client()
