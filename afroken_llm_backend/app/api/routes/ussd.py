"""
USSD entrypoint compatible with Africa's Talking-style callbacks.
"""

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse


# Router mounted under `/api/v1/ussd`.
router = APIRouter()


@router.post("/receive")
async def ussd_receive(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
):
    """
    Receive and respond to USSD requests in a simple menu flow.

    Parameters correspond to typical Africa's Talking USSD webhook fields:
    - `sessionId`: Unique identifier for the ongoing USSD session.
    - `serviceCode`: Shortcode dialed by the user (e.g. *123#).
    - `phoneNumber`: User's MSISDN.
    - `text`: User's input path through the menu, e.g. "1*2*12345".
    """

    # When `text` is empty, this is the first request in the session.
    if text == "":
        # "CON" prefix means "continue" (expect further user input).
        response = (
            "CON Karibu AfroKen\n"
            "1. NHIF\n"
            "2. KRA\n"
            "3. National ID\n"
            "4. Business\n"
            "5. Track Application\n"
            "98. Language\n"
            "99. Exit"
        )
    # User selected option 1 from the main menu.
    elif text == "1":
        response = "CON NHIF\n1. Check status\n2. Renew\n0. Back"
    # User navigated to "1*1" meaning "NHIF -> Check status".
    elif text == "1*1":
        response = "CON Ingiza NHIF number:"
    else:
        # "END" prefix tells the USSD gateway to terminate the session.
        response = "END Samahani, huduma bado haijaandaliwa."

    # Return a plain text response as required by USSD integrations.
    return PlainTextResponse(response)
