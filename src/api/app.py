import subprocess

from fastapi import FastAPI

from src.api.controllers import router as api_router
from src.api.stripe import router as stripe_router

nproc_res = subprocess.run("nproc", shell=True, capture_output=True, text=True)
print(nproc_res.stdout)

app = FastAPI()

app.include_router(api_router)
app.include_router(stripe_router)


# for dev purposes
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
