---
title: "NHIF Registration USSD and SMS Templates"
filename: "ussd_sms_nhif_registration.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["nhif", "ussd", "sms", "registration"]
---

# NHIF Registration USSD and SMS Templates

## USSD Menu Structure

**Main Menu:**
```
CON Karibu NHIF Services
1. Register
2. Check Status
3. Make Payment
4. Check Balance
0. Exit
```

**Registration Flow:**
```
CON Enter your ID Number:
[User enters ID]
CON Enter your Phone Number:
[User enters phone]
CON Registration successful. Your membership number is [NUMBER]. Pay KES 500 to activate.
```

**Payment Reminder:**
```
END Your NHIF contribution of KES 500 is due. Pay via M-Pesa Paybill 200222. Account: [MEMBERSHIP NUMBER]
```

**Status Check:**
```
END Membership: [NUMBER]. Status: Active. Last payment: [DATE]. Next due: [DATE]
```

## SMS Templates

**Registration Confirmation:**
```
NHIF: Registration successful. Membership: [NUMBER]. Pay KES 500 via M-Pesa Paybill 200222 to activate.
```

**Payment Confirmation:**
```
NHIF: Payment of KES [AMOUNT] received. Balance updated. Thank you.
```

**Reminder:**
```
NHIF: Your contribution of KES 500 is due by [DATE]. Pay via M-Pesa Paybill 200222. Account: [NUMBER]
```

**Status Update:**
```
NHIF: Your membership is [STATUS]. Last payment: [DATE]. Coverage valid until [DATE]
```

Sources:
- NHIF USSD and SMS service specifications

