from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
items_dic = {}

class Item(BaseModel):
    name: str
    price: float
    is_offer: Optional[bool] = None

@app.get("/")
def read_root():
    return {"Items": items_dic}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item": items_dic[item_id]}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    items_dic.update({item_id: item})
    return {"item_name": item.name, "item_price": item.price, "item_id": item_id}

@app.post("/items/{item_id}")
def post_item(item_id: int, item: Item):
    items_dic.update({item_id: item})
    return {"item_name": item.name, "item_price": item.price, "item_id": item_id}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    hold = items_dic.pop(item_id)
    return {"message": f"Item {item_id} has been removed from the database", "item": hold}
