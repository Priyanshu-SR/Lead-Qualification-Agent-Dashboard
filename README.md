# ⚡ LeadQ — Lead Qualification Dashboard

A privacy-first lead qualification dashboard for sales teams. Connects to your **n8n + WhatsApp + AI** pipeline — shows aggregate analytics to everyone, but individual lead details only when a specific phone number is searched.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## How It Works

```
WhatsApp → n8n Workflow → GPT Analysis → MongoDB
                                            ↑
                                     FastAPI reads
                                            ↓
                                   Dashboard (browser / Android app)
```

1. Customers chat on WhatsApp
2. n8n workflow captures messages into MongoDB (`customerChats` collection)
3. An AI agent (GPT) periodically analyses each conversation — writes qualification status, intent, confidence score, signals, and summary back into the document
4. **This app** reads MongoDB and presents aggregate analytics + per-lead lookup

---

## Dashboard Layout

### Top Section — Aggregate Analytics (always visible)

Every user sees the big-picture stats without access to individual leads:

| Card | Description |
|------|------------|
| Total Leads | Total number of analysed conversations |
| Qualified | Leads that asked about price, ROI, site visit, EMI, etc. |
| Unqualified | Leads that didn't show purchase intent |
| Qual. Rate | Percentage of qualified leads |
| Avg Confidence | Average AI confidence score across all leads |
| Total Messages | Combined message count across all conversations |

Plus an **Intent Breakdown Bar** showing the distribution of INTERESTED, QUERY, NOT_INTERESTED, JUNK, and FAILED intents.

### Bottom Section — Lead Lookup (search-gated)

- Sales agents enter a phone number (minimum 4 digits) to pull up a specific lead
- Only matching leads appear — **no browsing or scrolling through all leads**
- Phone numbers are **masked** on screen (e.g., `+91••••••••12`)
- Expanding a card reveals: AI summary, intent signals, and full chat history

### Privacy Controls

| Protection | How |
|-----------|-----|
| No lead browsing | Cards only render after a search with 4+ digits |
| Phone masking | Numbers displayed as `+XX••••••YZ` (first 2 + last 2 only) |
| No filter dropdowns | Status and intent filters are hidden from the UI |
| Aggregate-only stats | Top section shows totals, not individual data |
| API unchanged | Full data remains accessible via API for admin/manager use |

---

## Features

- **Privacy-first design** — sales agents see analytics but can't browse customer data
- **Search-gated access** — individual leads only appear when a specific number is searched
- **Phone number masking** — numbers are partially redacted on screen
- **6-card analytics dashboard** — total, qualified, unqualified, rate, confidence, messages
- **Intent breakdown bar** — color-coded distribution chart
- **Expandable lead details** — AI summary, signal chips, full chat history
- **Dark / Light theme** — sun/moon pill toggle with localStorage persistence
- **Fully responsive** — optimised for phones (380px+), tablets, laptops, and large monitors
- **Touch-optimised** — 44px minimum tap targets, no sticky hover on mobile
- **Notch-safe** — supports `safe-area-inset` for modern phones
- **Auto-refresh** — syncs every 45s (only re-fetches if search is active)
- **Chat caching** — expanded cards and loaded chats survive refresh cycles
- **Robust sessionId matching** — handles string, integer, regex, and scan fallback
- **Android APK** — optional WebView wrapper for native app distribution

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn |
| Database | MongoDB Atlas (via Motor async driver) |
| Frontend | Vanilla HTML/CSS/JS (single file, served by FastAPI) |
| Config | Pydantic Settings + `.env` file |
| AI Pipeline | n8n + OpenAI GPT (separate workflow) |
| Fonts | DM Sans, Playfair Display, JetBrains Mono |

---

## Project Structure

```
leadq/
├── main.py             # FastAPI app — API endpoints + serves dashboard
├── config.py           # Pydantic settings (reads .env)
├── dashboard.html      # Single-file responsive frontend
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
├── Procfile            # For Railway/Render deployment
├── LICENSE             # MIT license
└── android/            # Optional Android APK wrapper
    └── README.md       # Android build instructions
```

---

## Prerequisites

- **Python 3.10+**
- **MongoDB Atlas** cluster (or local MongoDB) with the `customerChats` collection populated by your n8n workflow
- **n8n** with the Lead Qualification Agent workflow running (writes `output` field to each document)

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/leadq.git
cd leadq
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
MONGO_URI=mongodb+srv://your_user:your_password@cluster0.xxxxx.mongodb.net/
MONGO_DB=test
MONGO_COLLECTION=customerChats
HOST=0.0.0.0
PORT=8000
```

### 5. Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open [http://localhost:8000](http://localhost:8000) — you should see the analytics dashboard with the search prompt below.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the dashboard HTML |
| `GET` | `/api/health` | DB connection status + document counts |
| `GET` | `/api/leads` | List leads with search, filter, sort, pagination |
| `GET` | `/api/leads/{sessionId}` | Single lead detail + full chat history |
| `GET` | `/api/stats` | Aggregated stats (totals, rates, intent breakdown) |

> **Note:** The API returns full unmasked data. Privacy controls (masking, search-gating) are enforced at the frontend layer only. Admin/manager tools can hit the API directly for complete data.

### `GET /api/leads` — Query Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `search` | string | — | Filter by phone number (digits extracted, regex match) |
| `qualified` | bool | — | Filter by `true` or `false` |
| `intent` | string | — | Filter: `INTERESTED`, `QUERY`, `NOT_INTERESTED`, `JUNK`, `FAILED` |
| `sort` | string | `desc` | Sort by analysedAt: `asc` or `desc` |
| `skip` | int | `0` | Pagination offset |
| `limit` | int | `50` | Results per page (max 200) |

### Example response — `GET /api/leads?search=9122`

```json
{
  "leads": [
    {
      "sessionId": "919220908612",
      "messageLength": 36,
      "analysedAt": "2026-02-08T14:05:00.000Z",
      "qualified": true,
      "intent": "INTERESTED",
      "confidence": 0.68,
      "signals": ["price", "location", "site_visit"],
      "summary": [
        "Asked about 2BHK price range",
        "Requested site visit on weekend",
        "Inquired about loan options"
      ]
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50,
  "hasMore": false
}
```

### Example response — `GET /api/stats`

```json
{
  "total": 150,
  "qualified": 87,
  "notQualified": 63,
  "qualificationRate": 0.58,
  "avgConfidence": 0.62,
  "avgMessages": 12.4,
  "intentBreakdown": {
    "INTERESTED": 52,
    "QUERY": 48,
    "NOT_INTERESTED": 30,
    "JUNK": 15,
    "FAILED": 5
  }
}
```

---

## MongoDB Document Schema

This is the schema your n8n workflow writes:

```json
{
  "sessionId": "919220908612",
  "messages": [
    {
      "type": "human",
      "data": { "content": "What is the price?" }
    },
    {
      "type": "ai",
      "data": { "content": "The price starts from..." }
    }
  ],
  "leadAnalysed": true,
  "analysedAt": "2026-02-08T14:05:00.000Z",
  "messageLength": 36,
  "output": {
    "qualified": true,
    "intent": "INTERESTED",
    "confidence": 0.68,
    "signals": ["price", "location"],
    "summary": ["Asked about price", "Requested site visit"]
  }
}
```

> `sessionId` can be stored as string or integer — the API handles both automatically via multi-strategy lookup (exact → int cast → regex → scan).

---

## Deployment

### Option A — VPS (Hostinger / DigitalOcean / AWS)

```bash
ssh root@your-server-ip
mkdir -p /opt/leadq && cd /opt/leadq
# upload files via scp or git clone
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
```

Create systemd service:

```bash
sudo nano /etc/systemd/system/leadq.service
```

```ini
[Unit]
Description=LeadQ Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/leadq
EnvironmentFile=/opt/leadq/.env
ExecStart=/opt/leadq/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable leadq
sudo systemctl start leadq
```

Add Nginx reverse proxy + SSL:

```bash
sudo nano /etc/nginx/sites-available/leadq
```

```nginx
server {
    listen 80;
    server_name leads.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/leadq /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d leads.yourdomain.com
```

### Option B — Railway / Render

Push to GitHub → connect repo → set env variables → deploy. The included `Procfile` handles the start command.

---

## Android App (Optional)

A WebView wrapper is available in the `android/` directory for distributing the dashboard as a native APK to your sales team.

Features: splash screen, pull-to-refresh, offline detection with retry, back button navigation, status bar theming.

See [`android/README.md`](android/README.md) for build instructions.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MONGO_URI` | ✅ | — | MongoDB connection string |
| `MONGO_DB` | ✅ | `test` | Database name |
| `MONGO_COLLECTION` | ✅ | `customerChats` | Collection name |
| `HOST` | ❌ | `0.0.0.0` | Server bind host |
| `PORT` | ❌ | `8000` | Server port |
| `CORS_ORIGINS` | ❌ | `["*"]` | Allowed CORS origins |

---

## Responsive Breakpoints

| Device | Breakpoint | Layout |
|--------|-----------|--------|
| Large monitors | ≥1441px | 1200px container, larger text |
| Laptop | 1025–1440px | 960px container (default) |
| Tablet | 641–1024px | Full-width, 3-col stats |
| Phone | 381–640px | 2-col stats, stacked search |
| Small phone | ≤380px | Compact everything, hide timestamps |
| Landscape phone | height ≤500px | Compressed header and stats |
| Touch devices | `pointer: coarse` | 44px tap targets, active states |
| Notched phones | `safe-area-inset` | Content avoids notch and home bar |

---

## n8n Workflow

The Lead Qualification Agent workflow (`Lead_Qualification_Agent.json`) runs on a schedule and:

1. Fetches unanalysed chats from MongoDB
2. Extracts human messages from each conversation
3. Sends them to GPT with a qualification prompt
4. Writes structured output (`qualified`, `intent`, `confidence`, `signals`, `summary`) back to the document

Import the workflow JSON into your n8n instance and configure:
- MongoDB credentials
- OpenAI API key

---

## Useful Commands

```bash
# Check if running
sudo systemctl status leadq

# Live logs
sudo journalctl -u leadq -f

# Restart after file changes
sudo systemctl restart leadq

# Test API
curl http://localhost:8000/api/health
curl http://localhost:8000/api/stats
curl "http://localhost:8000/api/leads?search=9122"
```

---

## Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/new-filter`)
3. Commit your changes (`git commit -m 'Add new filter option'`)
4. Push to the branch (`git push origin feature/new-filter`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
