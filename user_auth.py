
import os
import platform
import json
from cryptography.fernet import Fernet
from getmac import get_mac_address as gma
import requests

# Generate a key for encryption. This should be stored securely.
# For simplicity, we're generating it here. In a real app, you might
# want to store this key in a more secure way.
ENCRYPTION_KEY = b'KYQI7JBlCHvRAXaCj3hMpSETthP-1ZLSzQr74KEQcjU='
CIPHER_SUITE = Fernet(ENCRYPTION_KEY)

def get_syscfg_path():
    """
    Returns the absolute path for syscfg.dbx based on the operating system.
    """
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("ProgramData", "C:\ProgramData"), "ChambuPOS", "syscfg.dbx")
    else:
        # For Linux/macOS
        return os.path.join("/etc", "chambupos", "syscfg.dbx")

def check_syscfg_exists():
    """
    Checks if syscfg.dbx exists at the designated path.
    """
    path = get_syscfg_path()
    return os.path.exists(path)

def write_syscfg_file(phone_number, machine_fingerprint):
    """
    Creates the syscfg.dbx file with encrypted data.
    """
    path = get_syscfg_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {
        "phone_number": phone_number,
        "machine_fingerprint": machine_fingerprint
    }
    encrypted_data = CIPHER_SUITE.encrypt(json.dumps(data).encode())
    with open(path, 'wb') as f:
        f.write(encrypted_data)

def read_syscfg_file():
    """
    Reads and decrypts the syscfg.dbx file.
    """
    path = get_syscfg_path()
    try:
        with open(path, 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = CIPHER_SUITE.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())
    except Exception as e:
        print(f"Error reading or decrypting syscfg.dbx: {e}")
        return None

def get_machine_fingerprint():
    """
    Generates a unique machine fingerprint.
    """
    return gma()

def send_activation_request(name, phone):
    """
    Sends an activation request to the server.
    """
    url = "https://patanews.co.ke/pos/request_code.php"
    payload = {"name": name, "phone": phone}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": str(e)}

def verify_otp(phone, otp):
    """
    Verifies the OTP with the server.
    """
    url = "https://patanews.co.ke/pos/verify_code.php"
    payload = {"phone": phone, "otp": otp}
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": str(e)}
