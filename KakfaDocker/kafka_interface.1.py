#!/usr/bin/env python
import threading, logging, time
import multiprocessing
import json
from kafka import KafkaConsumer, KafkaProducer

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        # producer = KafkaProducer(bootstrap_servers='172.31.87.138:9092')
        producer = KafkaProducer(bootstrap_servers='172.31.87.138:9092', value_serializer=lambda m: json.dumps(m).encode('ascii'))

        while not self.stop_event.is_set():
            producer.send('test-python1', {'key': 'value'})
            time.sleep(1)

        producer.close()

class Consumer(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.stop_event = multiprocessing.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        consumer = KafkaConsumer(bootstrap_servers='172.31.87.138:9092',
                                 auto_offset_reset='earliest',
                                 consumer_timeout_ms=1000,
                                 value_deserializer=lambda m: json.loads(m.decode('ascii')))
        consumer.subscribe(['test-python1'])

        while not self.stop_event.is_set():
            for message in consumer:
                print(message)
                if self.stop_event.is_set():
                    break

        consumer.close()


def main():
    tasks = [
        Producer(),
        Consumer()
    ]

    for t in tasks:
        t.start()

    time.sleep(10)
    
    for task in tasks:
        task.stop()

    for task in tasks:
        task.join()
        
        
if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
        )
    main()