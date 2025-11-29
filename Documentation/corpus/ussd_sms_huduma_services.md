---
title: "Huduma Centre USSD and SMS Templates"
filename: "ussd_sms_huduma_services.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["huduma", "ussd", "sms", "services"]
---

# Huduma Centre USSD and SMS Templates

## USSD Menu Structure

**Main Menu:**
```
CON Karibu Huduma Kenya
1. Book Appointment
2. Check Status
3. Service Information
4. Find Centre
0. Exit
```

**Appointment Booking:**
```
CON Select Service:
1. ID Services
2. Passport
3. NHIF
4. KRA
[User selects]
CON Select Date: [DATES]
[User selects]
CON Appointment confirmed for [SERVICE] on [DATE] at [CENTRE]. Reference: [REF]
```

**Status Check:**
```
CON Enter Application Reference:
[User enters]
END Application [REF]: Status [STATUS]. Expected completion: [DATE]. Visit centre if delayed.
```

## SMS Templates

**Appointment Confirmation:**
```
Huduma: Appointment confirmed. Service: [SERVICE]. Date: [DATE]. Time: [TIME]. Centre: [LOCATION]. Reference: [REF]
```

**Reminder:**
```
Huduma: Reminder: Your appointment for [SERVICE] is on [DATE] at [TIME]. Bring original ID and required documents.
```

**Status Update:**
```
Huduma: Your [SERVICE] application [REF] is ready for collection. Visit [CENTRE] with ID to collect.
```

**Cancellation:**
```
Huduma: Appointment [REF] cancelled. To reschedule, dial *217# or visit hudumakenya.go.ke
```

Sources:
- Huduma Kenya USSD and SMS specifications

