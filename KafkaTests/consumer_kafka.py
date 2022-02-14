from confluent_kafka import Consumer, KafkaException, KafkaError
import sys, os
from avro_schema import UserModel

conf = {'bootstrap.servers': "96.37.182.148:9092,96.37.182.149:9092,96.37.182.150:9092",
        'group.id': "foo",
        'auto.offset.reset': 'latest'}

consumer = Consumer(conf)

running = True

def basic_consume_loop(consumer: Consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print(UserModel.deserialize(msg.value()))
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False

if __name__ == "__main__":
    try:
        basic_consume_loop(consumer, ['caleb_test'])
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    consumer.close()

