---
title: "County Services USSD and SMS Templates"
filename: "ussd_sms_county_services.md"
category: "ussd_sms"
jurisdiction: "Kenya"
lang: "en"
source: "synthesized"
last_updated: "2025-01-29"
tags: ["county", "ussd", "sms", "services"]
---

# County Services USSD and SMS Templates

## USSD Menu Structure

**Main Menu:**
```
CON Karibu [COUNTY] Services
1. Business Permit
2. Land Rates
3. Water Services
4. Health Services
0. Exit
```

**Business Permit:**
```
CON Business Permit Services:
1. Apply
2. Renew
3. Check Status
[User selects]
CON Enter Business Registration Number:
[User enters]
END Status: [STATUS]. Expires: [DATE]. Renew at county office or online.
```

**Land Rates:**
```
CON Enter Property Number:
[User enters]
END Property [NUMBER]: Outstanding KES [AMOUNT]. Pay via M-Pesa or county office.
```

## SMS Templates

**Business Permit Renewal:**
```
[COUNTY]: Your business permit expires [DATE]. Renew at county office or online to avoid penalties.
```

**Rates Payment:**
```
[COUNTY]: Land rates payment of KES [AMOUNT] received. Property [NUMBER]. Receipt: [REF]
```

**Service Update:**
```
[COUNTY]: [SERVICE] application [REF] approved. Collect at county office with ID. Valid [DAYS] days.
```

**Water Service:**
```
[COUNTY]: Water connection approved. Installation scheduled [DATE]. Meter number: [NUMBER]
```

Sources:
- County government USSD and SMS specifications

