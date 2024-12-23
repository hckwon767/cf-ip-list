import requests
import ipaddress
import json
import random
from pathlib import Path

def get_ip(url, key="", data={}, headers={}, cdn_name=""):
    """IP 정보를 주어진 URL에서 가져옵니다."""
    ips = ""
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # 2xx 상태 코드가 아닌 경우 예외 발생
        ip_info = response.json().get("info", []) # "info" 키가 없는 경우 빈 리스트 반환

        for i in ip_info:
            proxy_ip = i.get("ip")
            proxy_info = i.get("colo")
            if not proxy_ip or not proxy_info: #ip나 colo가 없을경우 continue
                continue
            try:
                if ipaddress.ip_address(proxy_ip).version == 6:
                    proxy_ip = f"[{proxy_ip}]"
            except ValueError:
                print(f"Invalid IP address: {proxy_ip}")
                continue
            ips += f"{proxy_ip}:443#{proxy_info}\n"

        if cdn_name:
            output_path = Path(f"{cdn_name}-ip.txt")
            output_path.write_text(ips, encoding="utf-8")
            print(f"{cdn_name}의 IP를 {output_path}에 저장했습니다.")

    except requests.exceptions.RequestException as e:
        print(f"{cdn_name}의 IP를 가져오는 중 오류 발생: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류: {e}")
        print(f"Response text: {response.text}")
        print(f"Response status code: {response.status_code}")


def get_cf_ip(url, headers):
    """HostMonit에서 Cloudflare IP를 가져옵니다 (기존 로직 유지)."""
    types = ["v4", "v6"]
    ips = ""
    for x in types:
        data = {"key": "iDetkOys"}
        if x == "v6":
            data["type"] = "v6"
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers)
            response.raise_for_status()
            ip_info = response.json().get("info", [])
        except requests.exceptions.RequestException as e:
            print(f"HostMonit IP 요청 오류: {e}")
            continue # 다음 타입으로 진행
        except json.JSONDecodeError as e:
            print(f"JSON 디코딩 오류: {e}")
            print(f"Response text: {response.text}")
            print(f"Response status code: {response.status_code}")
            continue

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
            print(f"cloudflare notls {port} 포트 파일을 {output_path}에 저장했습니다.")


def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "referer": "https://stock.hostmonit.com",
        "access-control-allow-origin": "https://stock.hostmonit.com",
        "origin": "https://stock.hostmonit.com",
        "content-type": "application/json",
    }
    cdn_data = {
        "cloudflare": [
            "https://www.182682.xyz/api/cf2dns/get_cloudflare_ip?type=v4",
            "https://www.182682.xyz/api/cf2dns/get_cloudflare_ip?type=v6",
        ]
    }
    hostmonit_url = "https://api.hostmonit.com/get_optimization_ip"

    for cdn_name, urls in cdn_data.items():
        for url in urls:
            data = {}
            if "v6" in url:
                data["type"] = "v6"
            get_ip(url, data=data, headers=headers, cdn_name=cdn_name)

    get_cf_ip(hostmonit_url, headers)

if __name__ == "__main__":
    main()
