import uvicorn
from database import get_matches, OrderBy, get_players
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# page: int = 0, 
#               limit: int = 50, 
#               users: str = "", 
#               name: str = "", 
#               case_sensitive: bool = False, 
#               order_by: str = OrderBy.START_TIME.name, 
#               is_asc: bool = False

@app.post("/mps")
async def mps(request: Request):
    body = await request.json()
    default_values = {
        "page": 0, 
        "limit": 25, 
        "users": "", 
        "beatmaps": "",
        "name": "", 
        "case_sensitive": False, 
        "order_by": OrderBy.START_TIME.name, 
        "is_asc": False
    }
    for k, v in default_values.items():
        if k not in body or type(body[k]) != type(v):
            body[k] = v

    if body["limit"] > 50:
        body["limit"] = 50
    elif body["limit"] < 1:
        body["limit"] = default_values["limit"]

    elif body["page"] < 0:
        body["page"] = default_values["page"]

    args = {
        "limit": body["limit"],
        "offset": body["page"] * body["limit"],
        "users": list(map(str.strip, body["users"].split(','))) if body["users"] else [],
        "beatmaps": list(map(str.strip, body["beatmaps"].split(','))) if body["beatmaps"] else [],
        "case_sensitive": body["case_sensitive"],
        "is_asc": body["is_asc"]
    }

    if o := OrderBy[body["order_by"].upper()]:
        args["order_by"] = o

    if len(body["name"]) > 1 and body["name"][0] == body["name"][-1] == '`':
        args["name"] = body["name"][1:-1]
        args["use_regex"] = True
    else:
        args["name"] = body["name"]
        args["use_regex"] = False

    return get_matches(**args)


@app.get("/players")
def players():
    return get_players()