from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from aredis import StrictRedis
import uvicorn

app = FastAPI()
client = StrictRedis(host='127.0.0.1', port=6379, db=0)

class CPE4(BaseModel):
    ipv4_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str

class CPE6(BaseModel):
    ipv6_address: str
    port_end: int
    port_start: int
    speedboost_trace_id: str
    action: str

class Item(BaseModel):
    #cm_mac: str
    qos_type: str
    router_ipv6_pd: str
    cpe_ipv4: CPE4
    cpe_ipv6: CPE6

class application():
    @app.get("/")
    async def read_root():
        return {"keys": await client.keys('*')}

    @app.get("/items/{item_id}")
    async def read_item(cm_mac: str):
        hold = await client.get(cm_mac)
        item = Item.parse_raw(hold)

        return {
            "cm_mac": cm_mac,
            "item": item.dict(),
        }

    @app.put("/items/{item_id}")
    async def update_item(cm_mac: str, item: Item):
        await client.getset(f'{cm_mac}', item.json())
        return {
            "cm_mac": cm_mac,
            "qos_type": item.qos_type,
            "router_ipv6_pd": item.router_ipv6_pd,
            "cpe_ipv4": item.cpe_ipv4,
            "cpe_ipv6": item.cpe_ipv6
        }

    @app.post("/items/{item_id}")
    async def post_item(cm_mac: str, item: Item):
        await client.set(f'{cm_mac}', item.json())
        assert await client.exists(f'{cm_mac}') is True
        return {
            "cm_mac": cm_mac,
            "qos_type": item.qos_type,
            "router_ipv6_pd": item.router_ipv6_pd,
            "cpe_ipv4": item.cpe_ipv4,
            "cpe_ipv6": item.cpe_ipv6
        }

    @app.delete("/items/{item_id}")
    async def delete_item(cm_mac: str):
        await client.delete(cm_mac)
        assert not await client.exists(f'{cm_mac}') is True
        return {"message": f"cm mac address: {cm_mac} has been removed from the database"}

    @app.delete("/delete_all/")
    async def delete_all():
        await client.flushdb()
        return {
            "message": f"All entries removed from database!",
            "keys": await client.keys('*')
        }

if __name__ == "__main__":
    app = application()
    uvicorn.run("fast_redis_combo:app", host="127.0.0.1", port=8000, log_level="info", workers=5)