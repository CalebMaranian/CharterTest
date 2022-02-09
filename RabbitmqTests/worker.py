import time
import aiormq, aiormq.abc
import sys, os, asyncio

def callback(message: aiormq.abc.DeliveredMessage):
    print(" [x] Received %r" % message.body)
    time.sleep(message.body.count(b'.'))
    print(" [x] Done")

async def main():
    connection = await aiormq.connect(url="amqp://guest:guest@127.0.0.1:5672/")

    channel = await connection.channel()
    await channel.basic_qos(prefetch_count=1)

    declare_ok = await channel.queue_declare(queue='task_queue1', durable=True)

    await channel.basic_consume(queue=declare_ok.queue, no_ack=True, consumer_callback=callback)


    #channel.start_consuming()

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

