---
title: "KRA Services USSD and SMS Templates"
filename: "ussd_sms_kra_services.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["kra", "ussd", "sms", "tax"]
---

# KRA Services USSD and SMS Templates

## USSD Menu Structure

**Main Menu:**
```
CON Karibu KRA Services
1. Check PIN Status
2. File Return
3. Make Payment
4. Check TCC Status
0. Exit
```

**PIN Verification:**
```
CON Enter your KRA PIN:
[User enters PIN]
END PIN: [PIN]. Status: Active. Name: [NAME]. File returns by 30th June.
```

**Payment Reminder:**
```
END Tax payment of KES [AMOUNT] due. Pay via M-Pesa Paybill 572572. Reference: [PIN]
```

**TCC Status:**
```
END TCC Status: [COMPLIANT/NON-COMPLIANT]. Expires: [DATE]. File returns to maintain compliance.
```

## SMS Templates

**Return Filing Reminder:**
```
KRA: Your tax return for [YEAR] is due by 30th June. File online at itax.kra.go.ke to avoid penalties.
```

**Payment Confirmation:**
```
KRA: Payment of KES [AMOUNT] received. Reference: [REF]. Balance: KES [BALANCE]. Thank you.
```

**TCC Generated:**
```
KRA: Your TCC is ready. Download from itax.kra.go.ke. Valid until [DATE]. Reference: [REF]
```

**PIN Registration:**
```
KRA: Your PIN [PIN] is registered. Access iTax at itax.kra.go.ke with your ID and password.
```

Sources:
- KRA USSD and SMS service specifications

