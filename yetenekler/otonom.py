import os
import requests
import subprocess

def batarya_durumu():
    try:
        bat_path = "/sys/class/power_supply/BAT0"
        if not os.path.exists(bat_path): bat_path = "/sys/class/power_supply/BAT1"
        if os.path.exists(bat_path):
            with open(f"{bat_path}/capacity", "r") as f: cap = f.read().strip()
            with open(f"{bat_path}/status", "r") as f: stat = f.read().strip()
            return int(cap), stat
    except: pass
    return None, None

def internet_tara():
    try:
        scan = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "dev", "wifi"], stderr=subprocess.DEVNULL).decode('utf-8')
        ssids = list(set([line.strip() for line in scan.split('\n') if line.strip() and line.strip() != '--']))
        return ssids[:3]
    except: return []
