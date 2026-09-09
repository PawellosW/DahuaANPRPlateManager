import re
import requests
from requests.auth import HTTPDigestAuth
import urllib3

# Wyłącz ostrzeżenia SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def validate_ip(ip):
    ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" \
                 r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return bool(re.match(ip_pattern, ip))


def test_connection(ip, username, password):
    try:
        url = f'https://{ip}/cgi-bin/recordFinder.cgi?action=find&name=TrafficRedList&count=1'
        response = requests.get(url, auth=HTTPDigestAuth(username, password), timeout=10, verify=False)
        # Debug
        print(f"[camera_manager] test_connection {ip} -> status {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"[camera_manager] Błąd połączenia: {e}")
        return False