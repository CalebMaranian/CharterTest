"""
This module combines fastapi with redis to create a web server app that integrates both technologies
"""

from typing import Dict, Union
from fastapi import FastAPI
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from aredis import StrictRedis
import uvicorn

app = FastAPI()
client = StrictRedis(host="127.0.0.1", port=6379, db=0)


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
    # cm_mac: str
    qos_type: str
    router_ipv6_pd: str
    cpe_ipv4: CPE4
    cpe_ipv6: CPE6


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


if __name__ == "__main__":
    app = Application()
    uvicorn.run("fast_redis_combo:app", host="127.0.0.1", port=8000, log_level="info")
