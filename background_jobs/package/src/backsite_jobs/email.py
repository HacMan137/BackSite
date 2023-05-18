import pika
import os
import sys
import json
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
from time import sleep
from traceback import print_exc

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
CONFIG_PATH = "/opt/configuration/config.json"
EMAIL_TEMPLATE_DIR = "/opt/configuration/email_templates"

with open(CONFIG_PATH, "r") as config_handle:
    CONFIG = json.loads(config_handle.read())

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
                print(f"Failed to connect to RabbitMQ. Sleeping and trying again")
                sleep(60)
        print("Connected to RabbitMQ")
        cls.channel.queue_declare(queue='email_jobs')
        cls.channel.basic_consume(queue='email_jobs', on_message_callback=cls.callback, auto_ack=True)
        cls.channel.start_consuming()

    @classmethod
    def send_verification_email(cls, username: str, email: str, secret: str):
        # Open HTML Email Template
        with open(f"{EMAIL_TEMPLATE_DIR}/email_verification_template.html", "r") as html_handle:
            html_template = html_handle.read()
        # Open TXT Email Template
        with open(f"{EMAIL_TEMPLATE_DIR}/email_verification_template.txt", "r") as txt_handle:
            txt_template = txt_handle.read()
        # Generate Verification URL
        if CONFIG["VERIFICATION_ENDPOINT"][0] != "/":
            CONFIG["VERIFICATION_ENDPOINT"] = "/" + CONFIG["VERIFICATION_ENDPOINT"]
        verification_url = f"{CONFIG['FRONTFACING_URL']}{CONFIG['VERIFICATION_ENDPOINT']}?key={secret}"
        # Fill out HTML template
        html_email = html_template.format(
            API_COMMON_NAME=CONFIG["API_COMMON_NAME"],
            USERNAME=username,
            VERIFICATION_URL=verification_url
        )
        # Fill out TXT template
        txt_email = txt_template.format(
            API_COMMON_NAME=CONFIG["API_COMMON_NAME"],
            USERNAME=username,
            VERIFICATION_URL=verification_url
        )
        # Send email
        cls.send_email(
            to_email=email, 
            subject=f"Verify your email address for {CONFIG['API_COMMON_NAME']}", 
            text_content=txt_email, 
            html_content=html_email
        )
        print(f"Verification email sent to {email}")
    
    @classmethod
    def callback(cls, ch, method, properties, body):
        '''
        Main callback function to handle any jobs received through RabbitMQ
        '''
        commandMap = {
            "sendVerificationEmail": cls.send_verification_email
        }
        print(f"Received body {body}")
        data = json.loads(body.decode())
        command = data['command']
        params = data["params"]
        if command in commandMap:
            try:
                commandMap[command](**params)
            except Exception as e:
                print(f"Error executing command {command}: {e}")
                print_exc()
        else:
            print(f"Error, unknown command {command}")

    @classmethod
    def send_email(cls, to_email: str, subject: str, text_content: str, html_content: str):
        #Generate email headers
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = CONFIG["API_EMAIL"]
        message["To"] = to_email
        # Add TXT and HTML email options
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        # Attach to message
        message.attach(part1)
        message.attach(part2)
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(CONFIG["SMTP_HOST"], CONFIG["SMTP_PORT"], context=context) as server:
            server.login(CONFIG["SMTP_USERNAME"], CONFIG["SMTP_PASSWORD"])
            server.sendmail(
                CONFIG["API_EMAIL"], to_email, message.as_string()
            )
        # Done
        return True