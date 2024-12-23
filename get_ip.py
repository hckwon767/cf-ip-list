import requests
import ipaddress
import json
import random
from pathlib import Path
import concurrent.futures  # 병렬 처리를 위한 모듈 추가

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

def fetch_ip_data(url, data=None):
    """URL에서 IP 데이터를 가져오는 함수"""
    try:
        if data:
            response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10) # 타임아웃 추가
        else:
            response = requests.get(url, headers=headers, timeout=10) # 타임아웃 추가
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def process_ip_info(response, cdn_name):
    """가져온 IP 정보를 처리하고 파일에 저장하는 함수"""
    if response is None:
        return

    ips = ""
    try:
        ip_info = response.json().get("info", [])
        is_json = True
    except json.JSONDecodeError:
        ip_info = response.text.strip().split('\n')
        is_json = False
        print(f"Warning: Non-JSON response from {response.url}. Treating as plain text.")
        print(f"Response text: {response.text}") # 디버깅을 위한 출력 추가
        is_json = False

    for i in ip_info:
        if is_json:
            proxy_ip = i.get("ip")
            proxy_info = i.get("colo")
            if not proxy_ip or not proxy_info:
                print(f"Warning: Missing 'ip' or 'colo' in JSON data: {i}")
                continue
        else:
            proxy_ip = i
            proxy_info = "N/A"

        try:
            ipaddress.ip_address(proxy_ip) # ip 유효성 검사만 진행
            if ":" in proxy_ip and "[" not in proxy_ip: # ipv6 주소이며 []로 감싸져 있지 않은 경우
                proxy_ip = f"[{proxy_ip}]"
        except ValueError:
            print(f"Invalid IP address: {proxy_ip}")
            continue
            
        ips += f"{proxy_ip}:443#{proxy_info}\n"

    if ips:
        output_path = Path(f"{cdn_name}-ip.txt")
        output_path.write_text(ips, encoding="utf-8")
        print(f"{cdn_name} IPs saved to {output_path}")

def process_cloudflare(url, data, cdn_name):
    response = fetch_ip_data(url, data)
    process_ip_info(response, cdn_name)


def process_hostmonit():
    url = "https://api.hostmonit.com/get_optimization_ip"
    types = ["v4", "v6"]
    ips = ""
    for x in types:
        data = {"key": "iDetkOys"}
        if x == "v6":
            data["type"] = "v6"

        response = fetch_ip_data(url, data)
        if response is None:
            continue

        try:
            ip_info = response.json().get("info", [])
        except json.JSONDecodeError:
            print(f"Error decoding JSON from Hostmonit (type {x}): {response.text}")
            continue

        for i in ip_info:
            proxy_ip = i.get("ip")
            proxy_info = i.get("colo")
            if not proxy_ip or not proxy_info:
                continue

            try:
                ipaddress.ip_address(proxy_ip)
                if ":" in proxy_ip and "[" not in proxy_ip:
                    proxy_ip = f"[{proxy_ip}]"
            except ValueError:
                print(f"Invalid IP address: {proxy_ip}")
                continue

            if x == "v6":
                ips += f"{proxy_ip}:443#{proxy_info} ipv6\n"
            else:
                ips += f"{proxy_ip}:443#{proxy_info}\n"
    if ips:
        print(ips)
        is_tls = ["443", "80"]
        for port in is_tls:
            output_path = Path(f"cloudflare-ip1{''.join(['-notls' if port == '80' else '', f'-{port}.txt'])}") # 간결하게 수정
            if port == "80":
                new_ips = ips.replace(":443", f":{random.choice(['80', '2052', '8080', '2082', '8880'])}")
                output_path.write_text(new_ips, encoding="utf-8")
            else:
                output_path.write_text(ips, encoding="utf-8")
            print(f"Cloudflare notls {port} port file saved to {output_path}")

def main():
    cdn_data = {
        "cloudflare": [
            {"url": "https://www.182682.xyz/api/cf2dns/get_cloudflare_ip?type=v4", "data":{}},
            {"url": "https://www.182682.xyz/api/cf2dns/get_cloudflare_ip?type=v6", "data": {"type": "v6"}},
        ],
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for cdn_name, url_data_list in cdn_data.items():
            for url_data in url_data_list:
                futures.append(executor.submit(process_cloudflare, url_data["url"], url_data["data"], cdn_name))
        concurrent.futures.wait(futures)

    process_hostmonit()

if __name__ == "__main__":
    main()
