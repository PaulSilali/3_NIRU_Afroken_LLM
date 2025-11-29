---
title: "Payment Reminders USSD and SMS Templates"
filename: "ussd_sms_payment_reminders.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["payment", "reminders", "ussd", "sms"]
---

# Payment Reminders USSD and SMS Templates

## USSD Menu Structure

**Payment Menu:**
```
CON Payment Services
1. NHIF Payment
2. KRA Tax Payment
3. HELB Repayment
4. County Rates
0. Exit
```

**Payment Instructions:**
```
CON Select Service:
[User selects]
END Pay KES [AMOUNT] via M-Pesa Paybill [NUMBER]. Account: [ACCOUNT]. Reference: [REF]
```

## SMS Templates

**NHIF Payment Reminder:**
```
NHIF: Your contribution of KES 500 is due by [DATE]. Pay via M-Pesa Paybill 200222. Account: [NUMBER]
```

**KRA Tax Reminder:**
```
KRA: Tax payment of KES [AMOUNT] due. Pay via M-Pesa Paybill 572572. Reference: [PIN]. Avoid penalties.
```

**HELB Repayment:**
```
HELB: Monthly repayment of KES [AMOUNT] due. Pay via M-Pesa Paybill 200800. Account: [ID NUMBER]
```

**County Rates:**
```
[COUNTY]: Land rates of KES [AMOUNT] due for property [NUMBER]. Pay at county office or M-Pesa.
```

**Final Reminder:**
```
[SERVICE]: Final reminder: Payment of KES [AMOUNT] overdue. Pay immediately to avoid service suspension.
```

Sources:
- Payment reminder service specifications

