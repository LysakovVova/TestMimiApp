import hmac, hashlib, time, json
from fastapi import FastAPI, HTTPException
import random
from pydantic import BaseModel
from urllib.parse import parse_qsl

app = FastAPI()
BOT_TOKEN = "7040597128:AAE2kqIGgmH0uZAhQpZlaq38XQnRJAXNr38"

class AuthReq(BaseModel):
    initData: str

def verify_init_data(init_data: str, max_age_sec: int = 3600) -> dict:
    data = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = data.pop("hash", None)
    if not received_hash:
        raise HTTPException(401, "No hash")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(401, "Bad signature")

    auth_date = int(data.get("auth_date", "0"))
    if auth_date <= 0 or (time.time() - auth_date) > max_age_sec:
        raise HTTPException(401, "Expired")

    return data

@app.post("/auth")
def auth(req: AuthReq):
    data = verify_init_data(req.initData)
    user = json.loads(data["user"])
    user_id = user["id"]

    # тут ты можешь загрузить профиль из БД
    balance = 100  # пример

    return {"user_id": user_id, "balance": balance}

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
