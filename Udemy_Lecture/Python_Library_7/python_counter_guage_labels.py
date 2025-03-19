from prometheus_client import (start_http_server,Summary,Counter,Gauge)
import random
import time

REQUEST_TIME=Summary(name="request_processing_second",documentation="Time Spent processing a function")
MY_GUAGE=Gauge(name="my_gauge",documentation="")
MY_COUNTER=Counter(name="my_counter_with_labels",documentation="",labelnames=["name","age"])


@REQUEST_TIME.time()
def process_request(t,n):
    MY_COUNTER.labels(name="ritish",age=35).inc(amount=n)
    MY_GUAGE.set(value=2)  # set the gauge
    MY_GUAGE.inc(amount=n)  # increase the gauge
    MY_GUAGE.dec(amount=n-1)  # decrease the gauge
    time.sleep(t)

start_http_server(port=8000)
process_request(t=random.random(),n=random.randint(a=1,b=10))
while True:
    A=1
print("The End")

