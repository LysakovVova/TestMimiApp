from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
from pydantic import BaseModel

app = FastAPI()

# Для теста можно разрешить всем:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # позже лучше сузить до GitHub URL
    allow_credentials=False,      # с "*" должно быть False
    allow_methods=["*"],
    allow_headers=["*"],
)

class EchoReq(BaseModel):
    value: str
class RangeReq(BaseModel):
    min: int
    max: int


@app.post("/number")
def number_range(req: RangeReq):
    if req.min > req.max:
        return {"error": "min > max"}

    n = random.randint(req.min, req.max)
    return {"number": n}



@app.post("/echo")
def echo(req: EchoReq):
    try:
        return {"value": str(int(req.value) ** 2)}
    except:
        return {"value": "не число"}
