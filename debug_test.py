#!/usr/bin/env python3

from fastapi.testclient import TestClient
from core.api.routes import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Test health endpoint
response = client.get('/v5/health')
print('Health Status:', response.status_code)
print('Health Content:', response.text)

# Test config endpoint  
response = client.get('/v5/config')
print('Config Status:', response.status_code)
print('Config Content:', response.text)