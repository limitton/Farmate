from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float

@app.get("/")
async def read_root():
    return "This is root path from MyAPI"

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str,  None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    result = {"item_id": item_id, **item.dict()}
    return result

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"deleted": item_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)