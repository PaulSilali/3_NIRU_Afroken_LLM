"""
Authentication / OTP demo endpoints.
"""

from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.schemas import TokenRequest, TokenVerify
from app.core.security import create_access_token
from app.config import settings


# Router that will be mounted under `/api/v1/auth`.
router = APIRouter()


@router.post("/token")
async def request_token(body: TokenRequest):
    """
    Request an OTP token for a given phone number (demo implementation).

    In a production system you would:
    - Randomly generate a secure OTP code.
    - Store the code server-side (e.g. DB/Redis) with expiry.
    - Send the OTP to the user via SMS provider (e.g. Africa's Talking).
    """

    # TODO: integrate real SMS provider and store OTP server-side.
    # For now we just return a message instructing the user to use a fixed code.
    return {"message": "OTP sent (demo). Use /verify with code 1234"}


@router.post("/verify")
async def verify(body: TokenVerify):
    """
    Verify an OTP code and return a bearer token if it is valid.

    This demo implementation accepts only the hard-coded code "1234".
    """

    # Check that the provided code matches the demo value.
    if body.code != "1234":
        # If incorrect, raise a 401 Unauthorized HTTP error.
        raise HTTPException(status_code=401, detail="Invalid code")

    # Create a JWT access token whose subject is the phone number.
    token = create_access_token(
        subject=body.phone_number,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MIN),
    )

    # Return the token and indicate that it is meant for Bearer auth usage.
    return {"access_token": token, "token_type": "bearer"}
