import sys, asyncio
import aiormq

async def main():
    connection = await aiormq.connect(url="amqp://guest:guest@127.0.0.1:5672/")
    channel = await connection.channel()

    declared_q = await channel.queue_declare(queue='task_queue1', durable=True)
    message = ' '.join(sys.argv[1:]) or "Hello World!"
    message = message.encode('utf-8')
    await channel.basic_publish(
        exchange='',
        routing_key=declared_q.queue,
        body=message,
        #properties=aiormq.spec.Basic.Properties(delivery_mode=1)
        )

    print(" [x] Sent %r" % message)

    await connection.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

