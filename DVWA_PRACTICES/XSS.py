import sys
import requests
from urllib.parse import quote

# 目标URL和参数（反射型XSS）
reflected_url = "http://10.1.10.2/vulnerabilities/xss_r/"
reflected_vun_param = 'name'

# 目标URL（存储型XSS）
stored_url = "http://10.1.10.2/vulnerabilities/xss_s/"

# XSS Payload
payload = "<h1>XSS</h1>"

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.63 Safari/537.36',
    'Cookie': 'security=low; PHPSESSID=bud3mjq30q9nqrk90e73qb9gmc'
}

# 构造数据（存储型XSS）
data = {
    'txtName': '1',
    'mtxMessage': payload,  # 对payload进行URL编码
    'btnSign': 'Sign+Guestbook'
}

try:
    # 发送反射型XSS请求并检测响应中是否包含payload
    reflected_full_url = f"{reflected_url}?{reflected_vun_param}={quote(payload)}"
    reflected_response = requests.get(reflected_full_url, headers=headers)
    if payload in reflected_response.text:
        print('检测到反射型XSS漏洞：', reflected_full_url)

    # 发送存储型XSS请求并检测响应中是否包含payload
    stored_response = requests.post(stored_url, data=data)
    if payload in stored_response.text:
        print('检测到存储型XSS漏洞：', stored_url)

except requests.RequestException as e:
    print('请求异常：', e)

print('测试payload:', payload)
sys.exit(0)
