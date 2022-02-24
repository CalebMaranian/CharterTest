"""
This module combines fastapi with redis to create a web server app that integrates both technologies
"""
from typing import Dict, Union
from fastapi import FastAPI
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from aredis import StrictRedis
import uvicorn
import aiormq
from dataclasses_avroschema import AvroModel
from dataclasses import dataclass
import os

redis_server = os.getenv("APP_SERVICE_PORT_6379_TCP_ADDR", "localhost")
redis_port = os.getenv("APP_SERVICE_SERVICE_PORT_REDIS_PORT", "6379")
rabbit_server = os.getenv("APP_SERVICE_PORT_5672_TCP_ADDR", "localhost")
rabbit_port = os.getenv("APP_SERVICE_PORT_5672_TCP_ADDR", "5672")
app = FastAPI()
client = StrictRedis(host=redis_server, port=redis_port, db=0)
futures = {}

class CPE4(BaseModel):
    """
    Description of CPE4 elements
    """
    ipv4_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str


class CPE6(BaseModel):
    """
    Description of CPE6 elements
    arg BaseModel:
    """
    ipv6_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str


class Item(BaseModel):
    """
    Description of Item elements
    """
    type: str
    qos_type: str
    router_ipv6_pd: str
    cpe_ipv4: CPE4
    cpe_ipv6: CPE6

@dataclass
class CPE4avro(AvroModel):
    """
    Description of CPE4 elements
    """
    ipv4_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str

@dataclass
class CPE6avro(AvroModel):
    """
    Description of CPE6 elements
    arg BaseModel:
    """
    ipv6_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str

@dataclass
class ItemAvro(AvroModel):
    """
    Description of Item elements
    """
    qos_type: str
    router_ipv6_pd: str
    cpe_ipv4: CPE4avro
    cpe_ipv6: CPE6avro

async def on_response(message:aiormq.abc.DeliveredMessage):
    item = message.body.decode()  #BaseModel.parse_raw(message.body).dict()
    print(f"Message received!\n{item}")

class Application:
    """
        This Application will allow users to edit data into a redis hash table
    """
    @staticmethod
    @app.get("/")
    async def read_root():
        """
            This method is the default apps web page and displays all keys currently in redis
        """
        return {"keys": await client.keys("*")}

    @staticmethod
    @app.get("/items/{item_id}")
    async def read_item(cm_mac: str):
        """
            This method will get the data a current mac address is
            pointing to in the redis hash table
                cm_mac: a str that represents a specific mac address
        """
        hold = await client.get(cm_mac)
        item = Item.parse_raw(hold)
        return {
            "cm_mac": cm_mac,
            "item": item.dict(),
        }

    @staticmethod
    @app.get("/secrets")
    async def read_secret():
        return {
            "Secret": os.getenv("SECRET_INFO", "No Secret Found")
        }

    @staticmethod
    @app.put("/items/{item_id}")
    async def update_item(cm_mac: str, item: Item) -> Dict[str, Union[str, CPE4, CPE6]]:
        """
            This method will replace the data a current mac address is pointing
             to in the redis hash table
                cm_mac: a str that represents a specific mac address
                item: an Item object containing information regarding the mac address
        """
        await client.getset(f"{cm_mac}", item.json())
        return {
            "cm_mac": cm_mac,
            "type": item.type,
            "qos_type": item.qos_type,
            "router_ipv6_pd": item.router_ipv6_pd,
            "cpe_ipv4": item.cpe_ipv4,
            "cpe_ipv6": item.cpe_ipv6,
        }

    @staticmethod
    @app.post("/items/{item_id}")
    async def post_item(cm_mac: str, item: Item) -> Dict[str, Union[str, CPE4, CPE6]]:
        """
            This method will add a new mac address to the redis hash table
                cm_mac: a str that represents a specific mac address
                item: an Item object containing information regarding the mac address
        """
        await client.set(f"{cm_mac}", item.json())
        assert await client.exists(f"{cm_mac}") is True
        return {
            "cm_mac": cm_mac,
            "type": item.type,
            "qos_type": item.qos_type,
            "router_ipv6_pd": item.router_ipv6_pd,
            "cpe_ipv4": item.cpe_ipv4,
            "cpe_ipv6": item.cpe_ipv6,
        }

    @staticmethod
    @app.delete("/items/{item_id}")
    async def delete_item(cm_mac: str) -> Dict[str, str]:
        """
            This method will delete a specific mac address from the redis hash table
                cm_mac: a str that represents a specific mac address
        """
        await client.delete(cm_mac)
        assert not await client.exists(f"{cm_mac}") is True
        return {
            "message": f"cm mac address: {cm_mac} has been removed from the database"
        }

    @staticmethod
    @app.delete("/delete_all/")
    async def delete_all() -> Dict[str, str]:
        """
            This method will call flushdb() and remove all entries from the redis database
        """
        await client.flushdb()
        return {
            "message": "All entries removed from database!",
            "keys": await client.keys("*"),
        }

    @staticmethod
    @app.post("/rabbit_test/{item_id}")
    async def post_to_rabbit(cm_mac: str) -> Dict:
        connection = await aiormq.connect(url=f"amqp://guest:guest@{rabbit_server}:{rabbit_port}/")
        channel = await connection.channel()
        hold = await client.get(cm_mac)
        item: Item = Item.parse_raw(hold)
        await channel.basic_publish(
            exchange="",
            body=item.json().encode("utf-8"),
            routing_key='queue_kafka1',
        )

        await connection.close()
        return {
            "message":  f'[x] Sent {cm_mac}"',
            "item": item.dict()
        }


if __name__ == "__main__":
    app = Application()
    uvicorn.run("fast_rabbit_kafka:app", host="0.0.0.0", port=8000, log_level="info")