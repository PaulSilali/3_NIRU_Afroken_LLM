from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse


router = APIRouter()


@router.post("/receive")
async def ussd_receive(
    sessionId: str = Form(...),
    serviceCode: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(""),
):
    """
    Simple Africa's Talking-compatible USSD entrypoint.
    """
    if text == "":
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
    elif text == "1":
        response = "CON NHIF\n1. Check status\n2. Renew\n0. Back"
    elif text == "1*1":
        response = "CON Ingiza NHIF number:"
    else:
        response = "END Samahani, huduma bado haijaandaliwa."
    return PlainTextResponse(response)



