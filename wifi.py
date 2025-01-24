import time

import network
import _thread
import socket
import ure

CONFIG_KEYS = ["IP address", "Subnet mask", "Gateway", "DNS server"]


class Wifi:
    def __init__(self):
        self.gate_state = None
        self.access_point_active = False
        self.http_server_active = False
        self.wifi_connected = False
        self.wlan = None

        self.new_request = False
        self.gate_action_request = None

    def set_gate_state(self, state):
        self.gate_state = state

    def get_gate_action_request(self):
        """
        Only call this once during each loop!
        Otherwise new_request will be reset and subsequent calls will be invalid.
        """
        if self.new_request:
            self.new_request = False
            return self.gate_action_request
        return None

    def connect(self, ssid, password):
        if self.access_point_active:
            print("AP active, deactivate it before connecting to a wifi network.")
            return

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(ssid, password)

        # Wait for connection
        max_attempts = 10
        attempt = 0
        while not self.wlan.isconnected() and attempt < max_attempts:
            print("Connecting to network...")
            time.sleep(1)
            attempt += 1

        if self.wlan.isconnected():
            self.wifi_connected = True
            print(f"Connected to '{ssid}'")
            network_config = dict(zip(CONFIG_KEYS, wlan.ifconfig()))
            print("Network config:")
            for key, value in network_config.items():
                print(f"  {key}: {value}")
            return True, network_config["IP address"]
        else:
            print("Failed to connect to network")
            return False, None

    def disconnect(self):
        self.wlan.disconnect()

    def create_access_point(self, ssid, password):
        if self.wifi_connected:
            print("Connected to a wifi network, disconnect before creating an AP")
            return

        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA2_PSK)

        # Wait for the AP to be active
        while not ap.active():
            print("Setting up access point...")
            time.sleep(1)

        print(f"Access point '{ssid}' created")
        self.access_point_active = True

        network_config = dict(zip(CONFIG_KEYS, ap.ifconfig()))
        print("Network config:")
        for key, value in network_config.items():
            print(f"  {key}: {value}")
        return True, network_config["IP address"]

    def start_http_server(self):
        if self.http_server_active:
            print("http server already active")
            return

        self.http_server_active = True
        _thread.start_new_thread(self._start_http_server, ())

    def stop_http_server(self):
        self.http_server_active = False

    def _start_http_server(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        print("Listening on", addr)

        while self.http_server_active:
            cl, addr = s.accept()
            print("HTTP request from:", addr)
            request = cl.recv(1024).decode("utf-8")
            request = str(request)

            # Parse the request to get the path
            request_line = request.split("\r\n")[0]
            method, path, _ = request_line.split()

            if method == "GET":
                # Extract query parameters
                match = ure.search(r"\?action=(\w+)", path)
                if match:
                    action = match.group(1).upper()
                    self.gate_action_request = action
                    self.new_request = True

            response = f"""\
HTTP/1.1 200 OK\r\n\
Content-Type: text/html\r\n\
Connection: close\r\n\
\r\n\
<html>\
<head>
    <title>ESP32</title>
        <style>
        body {{
            font-size: 64px;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
            font-family: sans-serif;
        }}
        .button-container {{
            display: flex;
            flex-direction: column;
            gap: 100px;
        }}
        .button {{
            font-size: 64px;
            display: inline-block;
            padding: 100px 200px;
            color: white;
            text-decoration: none;
            border-radius: 10px;
        }}
        .close-button {{
            background-color: #f44336;
        }}
        .open-button {{
            background-color: #4CAF50;
        }}
        .stop-button {{
            background-color: orange;
        }}
    </style>
</head>
<body>
<h1>Gate is<br> {self.gate_state}</h1>
<div class="button-container">
<button class="button open-button" onclick="fetch('/?action=OPEN').then(() => setTimeout(()=> window.location.reload(), 500)); return false;">Open</button>
<button class="button stop-button" onclick="fetch('/?action=STOP').then(() => setTimeout(()=> window.location.reload(), 500)); return false;">Stop</button>
<button class="button close-button" onclick="fetch('/?action=CLOSE').then(() => setTimeout(() => window.location.reload(), 500)); return false;">Close</button>
</div>
</body>
</html>
"""
            cl.send(response)
            cl.close()
