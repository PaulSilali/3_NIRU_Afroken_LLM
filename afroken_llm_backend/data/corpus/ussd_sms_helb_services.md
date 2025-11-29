---
title: "HELB Services USSD and SMS Templates"
filename: "ussd_sms_helb_services.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["helb", "ussd", "sms", "loan"]
---

# HELB Services USSD and SMS Templates

## USSD Menu Structure

**Main Menu:**
```
CON Karibu HELB Services
1. Check Balance
2. Make Payment
3. Application Status
4. Update Details
0. Exit
```

**Balance Check:**
```
CON Enter your ID Number:
[User enters ID]
END Loan Balance: KES [AMOUNT]. Monthly payment: KES [AMOUNT]. Pay via M-Pesa Paybill 200800.
```

**Payment Confirmation:**
```
END Payment of KES [AMOUNT] received. New balance: KES [BALANCE]. Thank you for repaying.
```

## SMS Templates

**Application Status:**
```
HELB: Your loan application [REF] is [STATUS]. Check helb.co.ke for details. Reference: [REF]
```

**Payment Reminder:**
```
HELB: Your monthly payment of KES [AMOUNT] is due. Pay via M-Pesa Paybill 200800. Account: [ID NUMBER]
```

**Balance Update:**
```
HELB: Payment of KES [AMOUNT] received. New balance: KES [BALANCE]. Keep repaying to clear loan faster.
```

**Disbursement:**
```
HELB: Loan disbursed to account [ACCOUNT]. Amount: KES [AMOUNT]. Check bank or M-Pesa. Reference: [REF]
```

Sources:
- HELB USSD and SMS service specifications

