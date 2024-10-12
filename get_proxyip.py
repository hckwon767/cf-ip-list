import requests
import ipaddress
import os
import shutil
import json
import random
import zipfile
import re
from pathlib import Path
#
headers={
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}
def get_cf_proxyip():
	url='https://zip.baipiao.eu.org'
	target_country = 'KR'
	data=requests.get(url,headers=headers)
	with open('cloudflare.zip','wb') as file:
		file.write(data.content)
		file.close()
	with zipfile.ZipFile('cloudflare.zip', 'r') as zip_ref:
		zip_ref.extractall('cf') 
	# 目标文件夹路径
	folder_path = Path('./cf')
	# 遍历文件夹中的所有文件
	tls_json=[]
	notls_json=[]
	for file_path in folder_path.rglob('*'):
		ports=re.split(r'-',file_path.stem)[-1]
		with open(file_path,'r',encoding='utf-8') as file:
			text=file.read()
			print(f'{ports}\n{text}')
			# news_text=text.replace('\n',f':{ports}\n')
			news_text=re.split(r'\n',text)
			del news_text[-1]
			if ports=='443':
				for i in news_text:
					ip_info=requests.get(f'https://ipinfo.io/{i}/json',headers=headers).json()
					country=ip_info['country']
					city=ip_info['city']
					org=ip_info['org']
					if country == target_country:
                    				tls_json.append({'ip': i, 'port': ports, 'colo': f'{country}'})
			else:
				for i in news_text:
					ip_info=requests.get(f'https://ipinfo.io/{i}/json',headers=headers).json()
					country=ip_info['country']
					city=ip_info['city']
					org=ip_info['org']
					if country == target_country:
                    				notls_json.append({'ip': i, 'port': ports, 'colo': f'{country}'})
			file.close()
	del tls_json[-1]
	del notls_json[-1]
	file_info={'cloudflare-proxyip-kr':tls_json,'cloudflare-proxyip-notls-kr':notls_json}
	for filename,ip_info1 in file_info.items():
		ips=''
		for j in ip_info1:
			ip=j['ip']
			port=j['port']
			colo=j['colo']
			ips=ips+f'{ip}#{colo}\n'
		with open(f'{filename}.txt','w') as file:
			file.write(ips)
			file.close()
	os.remove('./cloudflare.zip')
	shutil.rmtree('./cf')
get_cf_proxyip()
