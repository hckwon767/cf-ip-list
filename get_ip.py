import requests
import ipaddress
import json
import random
from pathlib import Path


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}


def get_ip_info(url, cdn_name):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        ip_info = response.json().get("info", [])
        return ip_info
    except requests.exceptions.RequestException as e:
        print(f"Error getting IP info for {cdn_name}: {e}")
        return []  # Empty list if request fails


def process_ip_info(ip_info, cdn_name):
    ips = ""
    for i in ip_info:
        proxy_ip = i.get("ip")
        proxy_info = i.get("colo")
        if not proxy_ip or not proxy_info:
            continue

        try:
            if ipaddress.ip_address(proxy_ip).version == 6:
                proxy_ip = f"[{proxy_ip}]"
        except ValueError:
            print(f"Invalid IP address: {proxy_ip}")
            continue

        ips += f"{proxy_ip}:443#{proxy_info}\n"

    if ips:
        output_path = Path(f"{cdn_name}-ip.txt")
        output_path.write_text(ips, encoding="utf-8")
        print(f"{cdn_name} IPs saved to {output_path}")


def get_cf_ip():
    url = "https://api.hostmonit.com/get_optimization_ip"
    types = ["v4", "v6"]
    ips = ""
    for x in types:
        data = {"key": "iDetkOys"}
        headers["referer"] = "https://stock.hostmonit.com"
        headers["access-control-allow-origin"] = "https://stock.hostmonit.com"
        headers["origin"] = "https://stock.hostmonit.com"
        headers["content-type"] = "application/json"
        if x == "v6":
            data["type"] = "v6"

        ip_info = requests.post(url, data=json.dumps(data), headers=headers).json().get("info", [])
        for i in ip_info:
            proxy_ip = i.get("ip")
            proxy_info = i.get("colo")
            if not proxy_ip or not proxy_info:
                continue

            try:
                if ipaddress.ip_address(proxy_ip).version == 6:
                    proxy_ip = f"[{proxy_ip}]"
            except ValueError:
                print(f"Invalid IP address: {  proxy_ip}")
                continue

            if x == "v6":
                ips += f"{proxy_ip}:443#{proxy_info} ipv6\n"
            else:
                ips += f"{proxy_ip}:443#{proxy_info}\n"

    print(ips)

    is_tls = ["443", "80"]
    for port in is_tls:
        if port == "443":
            output_path = Path("cloudflare-ip1.txt")
            output_path.write_text(ips, encoding="utf-8")
        else:
            ports = ["80", "2052", "8080", "2082", "8880"]
            new_ips = ips.replace(":443", f":{random.choice(ports)}")
            output_path = Path(f"cloudflare-ip1-notls-{port}.txt")
            output_path.write_text(new_ips, encoding="utf-8")
            print(f"cloudflare notls {port} port file saved to {output_path}")


def all_cdn():
    cdn_data = {
        "cloudflare": ["https://www.182682.xyz/api/cf2dns/get
