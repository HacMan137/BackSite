import pika
import os
import sys
from threading import Thread
from time import sleep

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

class EmailJobs:

    consumerThread = None
    shouldRun = False
    channel = None

    @classmethod
    def start(cls):
        cls.shouldRun = True
        cls.consumerThread = Thread(target=cls.__start_thread, daemon=True)
        cls.consumerThread.start()

    @classmethod
    def stop(cls):
        cls.shouldRun = False
        cls.channel.stop_consuming()
        cls.consumerThread.join()

    @classmethod
    def __start_thread(cls):
        print("Listening for email jobs.")
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
                cls.channel = connection.channel()
                break
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}. Sleeping and trying again")
                sleep(60)
        print("Connected to RabbitMQ")
        cls.channel.queue_declare(queue='email_jobs')
        cls.channel.basic_consume(queue='email_jobs', on_message_callback=cls.callback, auto_ack=True)
        cls.channel.start_consuming()
    
    @classmethod
    def callback(cls, ch, method, properties, body):
        print(f"Received body {body}")