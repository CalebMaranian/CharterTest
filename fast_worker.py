import time
import aiormq, aiormq.abc
import sys, os, asyncio
import uuid
from fast_rabbit_combo import Item

async def on_message(message: aiormq.abc.DeliveredMessage):
    item = Item.parse_raw(message.body).dict()
    time.sleep(3)
    print(" [x] Received %r" % item)
    time.sleep(message.body.count(b'.'))
    item["qos_type"] = "changed"
    #item_updated = Item.parse_obj(item)
    await message.channel.basic_publish(
        body=item["qos_type"].encode(), routing_key=message.header.properties.reply_to,
        properties=aiormq.spec.Basic.Properties(
            correlation_id=message.header.properties.correlation_id
        ),
    )
    await message.channel.basic_ack(message.delivery.delivery_tag)

    print(" [x] Done")

async def main():
    connection = await aiormq.connect(url="amqp://guest:guest@127.0.0.1:5672/")
    channel = await connection.channel()
    declare_ok = await channel.queue_declare(queue='queue_fast', durable=True)

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

