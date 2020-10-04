def load_requests(str,between=":",line="\n"):
	rc={}
	for x in str.split(line):
		if x=="":
			continue
		y=x.split(between)
		if len(y)==1:
			continue
		elif len(y)!=2:
			y[1]="".join(y[1:])
		rc[y[0]]=y[1]
	return rc
ua_txt="""IE6.0:Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)
IE7.0:Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)
IE8.0:Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1)
IE9.0:Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)
Firefox3.5:Mozilla/5.0 (compatible; rv:1.9.1) Gecko/20090702 Firefox/3.5
Firefox3.6:Mozilla/5.0 (compatible; rv:1.9.2) Gecko/20100101 Firefox/3.6
Firefox4.0:Mozilla/5.0 (compatible; rv:2.0) Gecko/20110101 Firefox/4.0
Firefox6.0:Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2
Chrome11.0:Mozilla/5.0 (compatible) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.682.0 Safari/534.21
Opera11.0:Opera/9.80 (compatible; U) Presto/2.7.39 Version/11.00
Maxthon3.0:Mozilla/5.0 (compatible; U) AppleWebKit/533.1 (KHTML, like Gecko) Maxthon/3.0.8.2 Safari/533.1
Android:Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 
iPhone:Mozilla/5.0 (iPhone; U; CPU OS 4_2_1 like Mac OS X) AppleWebKit/532.9 (KHTML, like Gecko) Version/5.0.3 Mobile/8B5097d Safari/6531.22.7
iPad:Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/4.0.2 Mobile/8C148 Safari/6533.18.5
Safari5.0:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_7) AppleWebKit/534.16+ (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4"""
ua_list=[]
for _x in ua_txt.split("\n"):
	ua_list.append(":".join(_x.split(":")[1:]))
def get_xes_url(url):
	import json,requests
	headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",'Content-Type': 'application/json'}
	c=requests.get(url,headers=headers)
	b = str(c.status_code)
	if b[:2] not in ["20","30"]:
		import xingyunlib.err
		xingyunlib.err.err("爬取失败！")
	else:
		return json.loads(c.text)
def spider(*args,**kwargs):
	import requests
	a=requests.get(*args,**kwargs)
	b=str(a.status_code)
	if b[:2] not in ["20","30"]:
		import xingyunlib.err
		xingyunlib.err.err(f"爬取错误，状态码：{b}")
		return
	return a

