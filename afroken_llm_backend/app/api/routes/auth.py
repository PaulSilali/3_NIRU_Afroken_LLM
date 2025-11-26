from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.schemas import TokenRequest, TokenVerify
from app.core.security import create_access_token
from app.config import settings


router = APIRouter()


@router.post("/token")
async def request_token(body: TokenRequest):
    """
    Demo OTP request endpoint.
    In production, generate and send an SMS OTP (e.g. via Africa's Talking).
    """
    # TODO: integrate real SMS provider and store OTP server-side
    return {"message": "OTP sent (demo). Use /verify with code 1234"}


@router.post("/verify")
async def verify(body: TokenVerify):
    """
    Demo verification endpoint that accepts a fixed OTP code.
    """
    if body.code != "1234":
        raise HTTPException(status_code=401, detail="Invalid code")

    token = create_access_token(
        subject=body.phone_number,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MIN),
    )
    return {"access_token": token, "token_type": "bearer"}



