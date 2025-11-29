---
title: "eCitizen Services USSD and SMS Templates"
filename: "ussd_sms_ecitizen_services.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["ecitizen", "ussd", "sms", "services"]
---

# eCitizen Services USSD and SMS Templates

## USSD Menu Structure

**Main Menu:**
```
CON Karibu eCitizen
1. Service Status
2. Book Appointment
3. Pay Fees
4. Help
0. Exit
```

**Service Status:**
```
CON Enter Application Reference:
[User enters]
END Application [REF]: Status [STATUS]. Expected: [DATE]. Visit ecitizen.go.ke for details.
```

**Appointment Booking:**
```
CON Select Service:
1. Passport
2. ID
3. Business Registration
[User selects]
CON Appointment available on [DATE]. Confirm? 1. Yes 2. No
```

## SMS Templates

**Application Submitted:**
```
eCitizen: Application [REF] submitted successfully. Track at ecitizen.go.ke. Expected: [DATE]
```

**Payment Required:**
```
eCitizen: Payment of KES [AMOUNT] required for [SERVICE]. Pay at ecitizen.go.ke or M-Pesa.
```

**Ready for Collection:**
```
eCitizen: Your [SERVICE] application [REF] is ready. Collect at [LOCATION] with ID. Valid 30 days.
```

**Reminder:**
```
eCitizen: Reminder: Your appointment for [SERVICE] is on [DATE]. Bring required documents.
```

Sources:
- eCitizen USSD and SMS specifications

