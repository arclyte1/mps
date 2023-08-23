import uvicorn
from fastapi import FastAPI
from tasks import load_mp

app = FastAPI()

@app.get("/request_mps")
async def index(start_id: int, end_id: int):
    if end_id - start_id > 10000:
        return {"message": "Too much mps requested (maximum is 10000)"}
    else:
        try:
            for i in range(start_id, end_id + 1):
                load_mp.apply_async((i,))
        except e:
            return {"message": str(e)}
        return {"message": "Tasks successfully added"}
