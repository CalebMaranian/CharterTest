import json

from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro
from confluent_kafka import Message as KafkaMessage
from confluent_kafka import KafkaError
from dataclasses_avroschema import AvroModel
import socket
from avro.schema import parse
import aiormq
import sys
import os
import asyncio
from fast_rabbit_kafka import Item, ItemAvro, CPE4avro, CPE6avro


async def on_message(message: aiormq.abc.DeliveredMessage):
    print(" [x] Received %r" % message.body.decode("utf-8"))
    #time.sleep(message.body.count(b'.'))

    conf = {
        "bootstrap.servers": "96.37.182.148:9092,96.37.182.149:9092,96.37.182.150:9092",
        "client.id": socket.gethostname(),
        "schema.registry.url": "http://96.37.182.148:8081"
    }
    producer = AvroProducer(conf)
    topic = "caleb_test"
    key_schema_str = """
    {
       "name": "key_test",
       "type": "string"
    }
    """
    item: Item = Item.parse_raw(message.body.decode("utf-8"))
    avro_obj = ItemAvro(
        qos_type=item.qos_type,
        router_ipv6_pd=item.router_ipv6_pd,
        cpe_ipv4=CPE4avro(
            ipv4_address=item.cpe_ipv4.ipv4_address,
            port_end=item.cpe_ipv4.port_end,
            port_start=item.cpe_ipv4.port_start,
            speedboost_trace_id=item.cpe_ipv4.speedboost_trace_id,
            action=item.cpe_ipv4.action,
        ),
        cpe_ipv6=CPE6avro(
            ipv6_address=item.cpe_ipv6.ipv6_address,
            port_end=item.cpe_ipv6.port_end,
            port_start=item.cpe_ipv6.port_start,
            speedboost_trace_id=item.cpe_ipv6.speedboost_trace_id,
            action=item.cpe_ipv6.action,
        ),
    )
    producer.produce(
        topic=topic,
        key="key_test",
        value=avro_obj.asdict(),
        value_schema=avro.loads(avro_obj.avro_schema()),
        key_schema=avro.loads(key_schema_str)
    )
    producer.poll(2)
    await message.channel.basic_ack(message.delivery.delivery_tag)
    print(" [x] Done")

async def main():
    connection = await aiormq.connect(url="amqp://guest:guest@localhost:30012/")
    channel = await connection.channel()
    declare_ok = await channel.queue_declare(queue='queue_kafka1', durable=False)

    await channel.basic_consume(
        queue=declare_ok.queue,
        consumer_callback=on_message
    )

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        print(' [*] Waiting for messages. To exit press CTRL+C')
        loop.run_forever()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

