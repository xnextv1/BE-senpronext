from fastapi import FastAPI, Request, Response

async def auth_check(request: Request):
    token = request.cookies.get('token')
    if not token:
        return {'token '}
    return {'token': token}