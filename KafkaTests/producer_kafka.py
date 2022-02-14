from confluent_kafka import Producer
import socket
from avro_schema import UserModel
import random

conf = {
    'bootstrap.servers': "96.37.182.148:9092,96.37.182.149:9092,96.37.182.150:9092",
    'client.id': socket.gethostname()
}

producer = Producer(conf)
topic = "caleb_test"
user = UserModel(
    name=random.choice(["Juan", "Peter", "Michael", "Moby", "Kim"]),
    age=random.randint(1, 50)
)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

producer.produce(topic, key="key_test", value=user.serialize(), callback=acked)

# Wait up to 1 second for events. Callbacks will be invoked during
# this method call if the message is acknowledged.
producer.poll(1)