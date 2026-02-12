# SzakiSzerviz PRO – CORE architektúra és adatmodell

## 0) Nagykép: egy CORE, három kimenet

A `SzakiSzerviz CORE` a központi motor (adat + workflow + napló), amely három üzleti irányt szolgál ki:

- **A) Saját cég belső rendszer**
- **B) SaaS/Eladás más szakiknak**
- **C) SzakiRadar piactér/platform**

```text
                ┌──────────────────────────────┐
                │        SZAKISZERVIZ CORE      │
                │  (adat + workflow + napló)    │
                └──────────────┬───────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
   ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼────────┐
   │ A) Saját cég   │   │ B) SaaS/Eladás│   │ C) SzakiRadar   │
   │ belső rendszer │   │ más szakiknak │   │ piactér/platform│
   └───────────────┘   └───────────────┘   └─────────────────┘
```

## 1) CORE belső működés: Adat → Esemény → Szabály → Művelet → Napló

A motor fő komponensei:

1. **Data Layer (Source of Truth)**
   - PostgreSQL (fő adatforrás)
   - Google Sheets (átmeneti / operatív nézetek)
   - Fájlok: PDF, képek, jegyzőkönyvek (Drive/Local)
2. **Event Bus / Események**
   - „Új munka rögzítve”
   - „Email kiküldve / visszapattant / válasz jött”
   - „Átutalás beérkezett”
   - „Helyszíni munka kész”
3. **Rules + Workflow Engine**
   - fix szabályok (if/then)
   - időablakok, grace, limit, csoportosítás
   - állapotgép (status)
4. **AI Layer (csak ahol értelme van)**
   - RAG dokumentum-visszakeresés
   - levél/szöveg klasszifikáció
   - kivonatolás: teendők és struktúrált mezők
   - generálás: ajánlat/levél/teljesítés-igazolás
5. **Actions / Kimenetek**
   - Email (Gmail/Brevo)
   - Push (OneSignal)
   - PDF/Word generálás
   - Sheet frissítés
   - feladat/emlékeztető létrehozása
6. **Audit Log / Napló**
   - mikor mi futott, miért, milyen inputtal
   - hibák + diagnosztika („miért nem küld?”)

## 2) Valós adatfolyam: „Új munka → kiosztás → visszajelzés → shortlist → pénz”

1. **Munka bejön**
   - űrlap / email / telefon / sheet sor
2. **Normalizer**
   - cím, kerület, szakma, sürgősség, határidő
   - duplikáció és hiányzó mezők jelzése
3. **Workflow: Munka kiosztása**
   - címzett kiválasztás (kerület + szakma + elérhetőség + terhelés)
   - limit (pl. 99-es batch, napi kvóta)
4. **Push: „Vállalod? IGEN/NEM”**
5. **Válaszok gyűjtése**
   - IGEN → shortlist
   - NEM / nincs válasz → következő kör
6. **Ajánlat generálás + kiküldés**
   - sablon + tételek + idő + kiszállás logika
7. **Státusz és pénz**
   - elfogadta / folyamatban / kész / számlázva / fizetve
   - automata emlékeztetők késésnél

## 3) Miért jó ez mindhárom iránynak?

### A) Saját cég (azonnali nyereség)
- kevesebb admin idő
- automata diagnosztika
- egységes dokumentumok
- visszakereshető napló

### B) Eladható rendszer (SaaS)
- ugyanaz a CORE, multi-tenant kiterjesztéssel
- jogosultsági modell (tulaj / admin / szerelő)
- konfigurálható sablonok és szabályok

### C) SzakiRadar platform
- munka-kiosztás és push logika mint piactéri mag
- reputáció, reakcióidő, sikerarány adatalapon
- később fizetési és jutalék logika ráépíthető

## 4) Ajánlott építési sorrend

1. CORE alap: státusz + napló + diagnosztika
2. Munka kiosztási folyamat véglegesítése
3. AI csak bemenet-értelmezésre (email/szöveg → struktúrált mezők)
4. Push + válasz + shortlist automatizmus

---

## 5) CORE adatmodell (mini-ERD)

```text
TENANT ──< USER
   │
   ├──< CONTACT ──< LOCATION
   │        │
   │        └──< JOB ──< JOB_ASSIGNMENT ──< RESPONSE
   │              │           │
   │              │           └──< MESSAGE (push/email/sms)
   │              │
   │              ├──< DOCUMENT
   │              ├──< WORKLOG (idő/anyag)
   │              ├──< PAYMENT (számla/pénz)
   │              └──< EVENT_LOG (audit/diagnosztika)
   │
   └──< TEMPLATE (email/pdf/ajánlat sablonok)
```

### 5.1 `tenant`
- `id` (uuid, pk)
- `name` (text)
- `timezone` (text, default: Europe/Budapest)
- `created_at`

### 5.2 `user`
- `id` (uuid)
- `tenant_id` (fk)
- `email` (text, tenanten belül unique)
- `name` (text)
- `role` (enum: `OWNER|ADMIN|TECH|FINANCE|VIEWER`)
- `phone` (text, optional)
- `is_active` (bool)
- `created_at`

### 5.3 `contact`
- `id`
- `tenant_id`
- `type` (enum: `CLIENT|PROPERTY_MANAGER|CARETAKER|CONTRACTOR|SUPPLIER`)
- `name`
- `email`
- `phone`
- `notes` (text)
- `tags` (`text[]`)
- `created_at`

### 5.4 `location`
- `id`
- `tenant_id`
- `contact_id` (fk, optional)
- `address_line`
- `zip`
- `city` (pl. Budapest)
- `district` (pl. VII)
- `lat` / `lng` (optional)
- `notes`

### 5.5 `job`
- `id`
- `tenant_id`
- `job_no` (text, tenanten belül unique)
- `title`
- `category` (enum: `ELECTRICAL|EON|MAINTENANCE|QUOTE|OTHER`)
- `service_type` (enum: `HIBAJAVITAS|FELULVIZSGALAT|KIJARAS|TELEPITES|TERVEZES`)
- `priority` (enum: `LOW|NORMAL|HIGH|URGENT`)
- `status` (enum, lásd lent)
- `contact_id` (fk)
- `location_id` (fk)
- `description_raw` (text)
- `description_norm` (jsonb)
- `created_by` (fk user)
- `created_at`
- `updated_at`

Javasolt `job.status` állapotgép:
`NEW → TRIAGE → ASSIGNING → SCHEDULED → IN_PROGRESS → DONE → INVOICED → PAID`

További állapotok: `BLOCKED`, `CANCELLED`.

### 5.6 `job_assignment`
- `id`
- `tenant_id`
- `job_id` (fk)
- `assignee_contact_id` (fk contact)
- `channel` (enum: `PUSH|EMAIL|SMS|PHONE`)
- `batch_id` (text)
- `sent_at`
- `expires_at`
- `state` (enum: `SENT|DELIVERED|RESPONDED|EXPIRED|FAILED`)
- `score` (numeric, optional)

### 5.7 `response`
- `id`
- `tenant_id`
- `job_assignment_id` (fk)
- `answer` (enum: `YES|NO|MAYBE`)
- `comment` (text)
- `responded_at`
- `meta` (jsonb)

### 5.8 `message`
- `id`
- `tenant_id`
- `job_id` (fk, optional)
- `direction` (enum: `OUT|IN`)
- `type` (enum: `EMAIL|PUSH|SMS`)
- `to_contact_id` (fk)
- `subject` (optional)
- `body`
- `provider` (enum: `GMAIL|BREVO|ONESIGNAL|OTHER`)
- `provider_msg_id`
- `status` (enum: `QUEUED|SENT|DELIVERED|BOUNCED|REPLIED|FAILED`)
- `sent_at`
- `received_at`
- `meta` (jsonb)

### 5.9 `document`
- `id`
- `tenant_id`
- `job_id` (fk)
- `type` (enum: `QUOTE|INVOICE|WORK_CERT|EON_FORM|PHOTO|OTHER`)
- `file_name`
- `storage_uri` (text)
- `hash` (text)
- `created_at`

### 5.10 `worklog`
- `id`
- `tenant_id`
- `job_id` (fk)
- `user_id` (fk, optional)
- `started_at`
- `ended_at`
- `minutes` (int)
- `labor_note` (text)
- `materials` (jsonb)
- `created_at`

### 5.11 `payment`
- `id`
- `tenant_id`
- `job_id` (fk)
- `type` (enum: `INVOICE|TRANSFER|CASH`)
- `invoice_no` (optional)
- `amount_gross` (numeric)
- `currency` (default: HUF)
- `status` (enum: `DUE|SENT|PARTIAL|PAID|OVERDUE`)
- `due_date` (optional)
- `paid_at` (optional)
- `meta` (jsonb)

### 5.12 `event_log`
- `id`
- `tenant_id`
- `job_id` (fk, optional)
- `scope` (enum: `EMAIL|PUSH|WORKFLOW|IMPORT|SYSTEM`)
- `level` (enum: `INFO|WARN|ERROR`)
- `event_type` (text, pl. `SEND_BLOCKED_TIMEWINDOW`)
- `reason_code` (text, pl. `TIMEWINDOW|UNSUB|BOUNCE|LIMIT|MISSING_DATA`)
- `message` (emberi magyarázat)
- `data` (jsonb, input/output snapshot)
- `created_at`

## 6) Minimál FastAPI endpoint-javaslatok

- `POST /jobs` – új munka rögzítése
- `POST /jobs/{id}/triage` – AI normalizálás
- `POST /jobs/{id}/assign` – kiosztás indítása
- `POST /assignments/{id}/response` – IGEN/NEM visszajelzés
- `POST /messages/send` – email/push/sms küldés
- `GET /diagnostics/sendability?job_id=...` – küldhetőség diagnosztika
- `POST /documents/generate` – PDF/Word generálás
- `POST /payments/import` – utalási sorok importja
