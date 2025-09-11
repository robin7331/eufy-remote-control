import network
import asyncio
from credentials import ssid, password
from umqtt.simple import MQTTClient
import ujson
import utime

class ConnectionState:
    DISCONNECTED = 0
    CONNECTING_WIFI = 1
    CONNECTING_MQTT = 2
    CONNECTED = 3
    ERROR = 4

class PingState:
    IDLE = 0
    PRINTING_12MM = 1
    PRINTING_16MM = 2
    ERROR_12MM = 3
    ERROR_16MM = 4
    STOPPING_12MM = 5
    STOPPING_16MM = 6
    TIMEOUT = 7

class ConnectionManager:
    def __init__(self, broker_ip, broker_port, client_id='button-box', status_topic='uv_studio/status', command_topic='uv_studio/command', control_topic='uv_studio/control'):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.client_id = client_id
        self.status_topic = status_topic
        self.command_topic = command_topic
        self.control_topic = control_topic
        self.connection_state = ConnectionState.DISCONNECTED
        self.ip_address = None
        self.mqtt_client = None

        self.on_connection_changed = None
        self.on_trigger_servo = None
        self.on_ping_changed = None
        on_servo_parameters_received = None

        self.last_ping_received = utime.ticks_ms()
        self.last_ping_contents = None
        self.last_ping_processed_at = utime.ticks_ms()
        self.ping_state = None
        
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)


    def set_on_connection_changed(self, callback):
        self.on_connection_changed = callback
        if self.on_connection_changed:
            self.on_connection_changed(self, self.connection_state)

    def set_on_trigger_servo(self, callback):
        self.on_trigger_servo = callback

    def set_on_servo_parameters_received(self, callback):
        self.on_servo_parameters_received = callback

    def set_on_ping_changed(self, callback):
        self.on_ping_changed = callback

    def _set_connection_state(self, state):
        if state is self.connection_state:
            return
        
        self.connection_state = state
        if self.on_connection_changed:
            self.on_connection_changed(self, state)

    def _set_ping_state(self, state):
        if state is self.ping_state:
            return
        
        self.ping_state = state
        if self.on_ping_changed:
            self.on_ping_changed(self, state)

    async def connect(self):
        self._set_connection_state(ConnectionState.CONNECTING_WIFI)
                  
        # Connect to your network
        self.wlan.connect(ssid, password)

        # Wait for Wi-Fi connection
        connection_timeout = 30
        while connection_timeout > 0:
            if self.wlan.status() >= 3:
                return True
            connection_timeout -= 1
            await asyncio.sleep(1)

        return False
    
    
    def _mqtt_callback(self, topic, msg):
            try:
              topic = topic.decode('utf-8')
            except Exception as e:
              print('Error decoding topic:', e) 
              return # Exit the function if decoding fails

            try :
              message = ujson.loads(msg)
            except Exception as e:
              print('Error decoding message:', e)
              return
            
            if topic == self.control_topic:
              if message["action"] == "press_start_button" and self.on_trigger_servo:
                  self.on_trigger_servo()

              if message["action"] == "set_servo_parameters" and self.on_servo_parameters_received:
                  self.on_servo_parameters_received(message["retracted_angle"], message["extended_angle"])

            elif topic == self.status_topic:
              self.last_ping_contents = message
              self.last_ping_received = utime.ticks_ms()

    
    async def _connect_mqtt(self):
        self.mqtt_client = MQTTClient(self.client_id, self.broker_ip, self.broker_port)
        self.mqtt_client.set_callback(self._mqtt_callback)
        try:
          self.mqtt_client.connect()
        except Exception as e:
          print('Error connecting to MQTT broker:', e)
          self._set_connection_state(ConnectionState.ERROR)
          return
        
        self.mqtt_client.subscribe(self.status_topic)
        self.mqtt_client.subscribe(self.control_topic)
        self._set_connection_state(ConnectionState.CONNECTED)

    def send_mqtt_command(self, command):
        if self.connection_state is not ConnectionState.CONNECTED or not self.mqtt_client:
            print('Not connected, cannot send command')
            return False
        
        try:
            self.mqtt_client.publish(self.command_topic, b'{"command": "%s"}' % command)
            return True
        except Exception as e:
            print('Error publishing MQTT message:', e)
            self._set_connection_state(ConnectionState.ERROR)
            return False
    
    def tick(self):
        status = self.wlan.status()

        if status is network.STAT_IDLE:
              self._set_connection_state(ConnectionState.DISCONNECTED)

        if status is network.STAT_CONNECTING:
              self._set_connection_state(ConnectionState.CONNECTING_WIFI)

        if status is network.STAT_WRONG_PASSWORD or status is network.STAT_NO_AP_FOUND or status is network.STAT_CONNECT_FAIL:
              self._set_connection_state(ConnectionState.ERROR)

        if status is network.STAT_GOT_IP:
              if not self.ip_address:
                  network_info = self.wlan.ifconfig()
                  self.ip_address = network_info[0]
                  print('Connected, IP address:', self.ip_address)
                  self._set_connection_state(ConnectionState.CONNECTING_MQTT)
                  asyncio.run(self._connect_mqtt())
                  

        # Check for new MQTT messages
        if self.connection_state is ConnectionState.CONNECTED and self.mqtt_client:
          self.mqtt_client.check_msg()


        # Process the pings every second
        if utime.ticks_ms() - self.last_ping_processed_at > 1000:
            self.last_ping_processed_at = utime.ticks_ms()

            # if the last ping is over 10 seconds old there is an error
            if self.last_ping_received and (utime.ticks_ms() - self.last_ping_received) > 10000:
                self._set_ping_state(PingState.TIMEOUT)
            else:
              if self.last_ping_contents:
                  if self.last_ping_contents["print_running"] == "12mm":
                      self._set_ping_state(PingState.PRINTING_12MM)
                  elif self.last_ping_contents["print_running"] == "16mm":
                      self._set_ping_state(PingState.PRINTING_16MM)
                  elif self.last_ping_contents["print_running"] == "error_12mm":
                      self._set_ping_state(PingState.ERROR_12MM)
                  elif self.last_ping_contents["print_running"] == "error_16mm":
                      self._set_ping_state(PingState.ERROR_16MM)
                  elif self.last_ping_contents["print_running"] == "stopping_12mm":
                      self._set_ping_state(PingState.STOPPING_12MM)
                  elif self.last_ping_contents["print_running"] == "stopping_16mm":
                      self._set_ping_state(PingState.STOPPING_16MM)
                  elif self.last_ping_contents["print_running"] == False:
                      self._set_ping_state(PingState.IDLE)
                  else: 
                      self._set_ping_state(PingState.TIMEOUT)
                


