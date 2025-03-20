from prometheus_client import push_to_gateway, CollectorRegistry, Gauge
import time

registry = CollectorRegistry()  # Create a registry
guage = Gauge(name='python_push_to_gateway',
              documentation='Last time a batch job successfully finished', 
              registry=registry,)  # Create a gauge metric

while True:
    guage.set_to_current_time()  # Set the current time

    push_to_gateway(gateway="localhost:9091", job="Job A", registry=registry)  # Push the metric to the gateway

