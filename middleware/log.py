from fastapi import FastAPI, Request, Response

async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url} {request.client.host}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response