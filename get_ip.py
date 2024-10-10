import requests
import ipaddress
import os
import json
import random
import zipfile
import re
from pathlib import Path


headers={
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}
def all_cdn():
	data={
		# 'cloudflare':['https://monitor.gacjie.cn/api/client/get_ip_address?cdn_server=1&type=v4','https://monitor.gacjie.cn/api/client/get_ip_address?cdn_server=1&type=v6'],
		# 'cloudfront':['https://monitor.gacjie.cn/api/client/get_ip_address?cdn_server=2&type=v4','https://monitor.gacjie.cn/api/client/get_ip_address?cdn_server=2&type=v6'],
		'cloudflare':['https://www.182682.xyz/api/cf2dns/get_cloudflare_ip?type=v4','https://www.182682.xyz/api/cf2dns/get_cloudflare_ip?type=v6'],
		# 'cloudfront':['https://www.182682.xyz/api/cf2dns/get_cloudfront_ip?type=v4','https://www.182682.xyz/api/cf2dns/get_cloudfront_ip?type=v6'],
		# 'gcore':['https://monitor.gacjie.cn/api/client/get_ip_address?cdn_server=3&type=v4','https://monitor.gacjie.cn/api/client/get_ip_address?cdn_server=3&type=v6'],
	}
	for key,value in data.items():
		print(key)
		ips=''
		for x in value:
			get_info=requests.get(x,headers=headers).json()
			get_cm=get_info['info']['CM']
			get_cu=get_info['info']['CU']
			get_ct=get_info['info']['CT']
			get_info_list=get_cm+get_cu+get_ct
			# print(get_info_list)
			if get_info_list==[]:
				break
			for i in get_info_list:
				proxy_ip=i['ip']
				proxy_info=i['colo']
				try:
				    check_ip=ipaddress.IPv6Address(proxy_ip)
				    proxy_ip=f'[{proxy_ip}]'
				except Exception as e:
					pass
				ips=ips+f'{proxy_ip}:443#{proxy_info}\n'
		print(ips)
		with open(f'{key}-ip.txt','w') as file:
			file.write(ips)
			file.close()

def get_cf_ip():
	url='https://api.hostmonit.com/get_optimization_ip'
	types=['v4']
	ips=''
	for x in types:
		data={'key': 'iDetkOys'}
		headers['referer']='https://stock.hostmonit.com'
		headers['access-control-allow-origin']='https://stock.hostmonit.com'
		headers['origin']='https://stock.hostmonit.com'
		headers['content-type']='application/json'
		if x=='v6':
			data['type']='v6'
		ip_info=requests.post(url,data=json.dumps(data),headers=headers).json()['info']
		# print(ip_info)
		for i in ip_info:
			proxy_ip=i['ip']
			proxy_info=i['colo']
			try:
			    check_ip=ipaddress.IPv6Address(proxy_ip)
			    proxy_ip=f'[{proxy_ip}]'
			except Exception as e:
				pass
			ips=ips+f'{proxy_ip}:443#{proxy_info}\n'
		print(ips)
		is_tls=['443','80']
		for x in is_tls:
			if x=='443':
				with open('cloudflare-ip1.txt','w') as file:
					file.write(ips)
			else:
				ports=['80','2052','8080','2082','8880']
				news_ips=ips.replace(':443',f':{random.choice(ports)}')
				with open('cloudflare-ip1-notls.txt','w') as file:
					file.write(news_ips)
					file.close()
		
all_cdn()
get_cf_ip()
