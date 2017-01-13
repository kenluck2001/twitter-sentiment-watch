import httplib
import json
import time
from datetime import datetime


conn = httplib.HTTPConnection("qgsapp.herokuapp.com")

for i in range(1,10):
	data = { "status": 1, "timestamp": datetime.now().isoformat() }
	headers = {"Content-type": "application/json", "Accept": "text/plain", "Connection":" keep-alive"}
	conn.request("POST", "/trump", json.dumps(data), headers)
	r = conn.getresponse()
	r.read()
	time.sleep(10)
#conn.request("GET", "/trump")