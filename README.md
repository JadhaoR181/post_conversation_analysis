
# Post Conversation Analysis – Internship Assignment (Kipps.AI)

### 🚀 Developed by: Ravindra Jadhav  
**Role:** Full Stack Developer Intern (Assignment Submission)  
**Tech Stack:** Django REST Framework, Python, SQLite, Cron Automation  

---

## 📌 Overview

This project implements a **Post Conversation Analysis** system that evaluates customer support chats between a **user** and an **AI assistant**.  
It analyzes chat logs and computes various quality metrics like **clarity**, **relevance**, **empathy**, **sentiment**, and more.

The application supports:
- ✅ Uploading chat data as raw JSON or `.json` file  
- ✅ Automatic analysis of conversation quality  
- ✅ Daily scheduled automation (via cron or API trigger)  
- ✅ Retrieving historical reports via REST API  

---

## 🏗️ Project Architecture

```
post_conversation_analysis/
│
├── analysis/
│   ├── models.py              # Conversation, Message, ConversationAnalysis
│   ├── serializers.py         # Serializers for REST API
│   ├── views.py               # API logic (upload, analyze, reports)
│   ├── analysis_engine.py     # Core logic for computing metrics
│   ├── cron.py                # Daily automation function
│
├── pca/
│   ├── settings.py            # Project settings
│   ├── urls.py                # API routes
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions (for reviewer/interviewer)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/JadhaoR181/post_conversation_analysis.git
cd post_conversation_analysis
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations
```bash
python manage.py migrate
```

### 5️⃣ Run the development server
```bash
python manage.py runserver
```

✅ The backend is now running at:
```
http://127.0.0.1:8000
```

---

## 🔌 API Endpoints

### 🟢 1. Upload Conversation (JSON or File)
**Endpoint:** `POST /api/conversations/`  
**Description:** Accepts either raw JSON or a `.json` file upload.

#### 🔸 JSON Body Example
```json
{
  "title": "Support Chat - Order Delay",
  "messages": [
    {"sender": "user", "message": "My order is late, can you check?"},
    {"sender": "ai", "message": "Sure! Please share your order ID."},
    {"sender": "user", "message": "ORD123456"}
  ]
}
```

**Response:**
```json
{"conversation_id": 1, "status": "Conversation stored successfully"}
```

#### 🔸 File Upload Example (Postman)
- Type: `form-data`
- Key: `file`
- Value: Attach `.json` file (same structure as above)

---

### 🟢 2. Analyze Conversation
**Endpoint:** `POST /api/analyse/`  
**Body Example:**
```json
{"conversation_id": 1}
```

**Response Example:**
```json
{
  "clarity_score": 0.83,
  "relevance_score": 0.74,
  "accuracy_score": 0.88,
  "completeness_score": 1.0,
  "sentiment": "positive",
  "empathy_score": 0.6,
  "fallback_count": 0,
  "resolution": true,
  "overall_score": 0.81
}
```

---

### 🟢 3. Get All Reports
**Endpoint:** `GET /api/reports/`

**Response Example:**
```json
[
  {
    "conversation": {"id": 1, "title": "Support Chat - Order Delay"},
    "clarity_score": 0.83,
    "overall_score": 0.81,
    "sentiment": "positive"
  }
]
```

---

### 🟢 4. Trigger Daily Automation (Manual or via Cron)
**Endpoint:** `GET /api/trigger-daily-analysis/`  
**Response:**
```json
{"status": "Daily analysis triggered successfully"}
```

---

## 🤖 Analysis Metrics Explanation

| Metric | Description |
|---------|-------------|
| **Clarity Score** | Based on sentence length and structure of AI messages. |
| **Relevance Score** | Measures keyword overlap between user and AI replies. |
| **Accuracy Score** | Detects confident vs uncertain words in AI messages. |
| **Completeness Score** | Checks if conversation ends with closure or gratitude. |
| **Empathy Score** | Detects empathy-related words like "sorry" or "understand". |
| **Sentiment** | Analyzed from user messages using VADER sentiment analyzer. |
| **Fallback Count** | Counts AI responses like "I don’t know" or "not sure". |
| **Resolution Flag** | True if AI indicates issue is resolved. |
| **Overall Score** | Weighted average of all available metrics. |

---

## 🕓 Automation Setup (Daily Scheduled Analysis)

### 🔹 Windows-Compatible Automation
Since `django-crontab` doesn’t work on Windows,  
a **cloud scheduler** is used via [cron-job.org](https://cron-job.org/en/).

Steps:
1. Run your Django server and expose it via **ngrok**:
   ```bash
   ngrok http 8000
   ```
   
   Example public URL:
   ```
   https://acorned-florence-unwilled.ngrok-free.dev
   ```

2. Add this URL to `ALLOWED_HOSTS` in `settings.py`:
   ```python
   ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.ngrok-free.dev']
   ```

3. Register your API endpoint in cron-job.org:
   ```
   https://acorned-florence-unwilled.ngrok-free.dev/api/trigger-daily-analysis/
   ```
   Set to **run every day** and add header:
   ```
   ngrok-skip-browser-warning: true
   ```

✅ Result: Daily automation works even on Windows.

---

## 💬 Automation Strategy – Choice Explanation

For this internship project:
> I implemented **cron-job.org + endpoint** automation, since it’s simple, platform-independent, and perfect for local or demo environments.  
> In a production setup, I would use **Celery + Beat** for internal, reliable scheduling and retry mechanisms.

---

## 🧪 Testing Guide

1. Start the Django server:  
   ```bash
   python manage.py runserver
   ```

2. Test endpoints using **Postman**:
   - `/api/conversations/` → Upload JSON or file  
   - `/api/analyse/` → Analyze stored conversation  
   - `/api/reports/` → Fetch analysis results  
   - `/api/trigger-daily-analysis/` → Trigger daily reanalysis  

3. Confirm the results in Postman or Django Admin.

---

## 🧾 Example Output

```json
{
  "clarity_score": 0.473,
  "relevance_score": 0.444,
  "accuracy_score": 0.88,
  "completeness_score": 1.0,
  "sentiment": "positive",
  "empathy_score": 0.6,
  "fallback_count": 0,
  "resolution": true,
  "overall_score": 0.666
}
```

---

## 🧠 Interview Talking Points

- Unified file and JSON input into a **single endpoint** using `MultiPartParser` and `JSONParser`.  
- Implemented heuristic-based metrics without external ML models.  
- Built a **daily automation trigger** compatible with Windows.  
- Used Django REST Framework best practices (models, serializers, views).

---

## 🧰 Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend Framework** | Django REST Framework |
| **Database** | SQLite |
| **Automation** | django-crontab / cron-job.org |
| **Sentiment Analysis** | VADER (NLTK) |
| **Language** | Python 3.12 |
| **Version Control** | Git & GitHub |

---

## 🏁 Final Notes

✅ All assignment parts completed:  
- **Part 1:** Post Conversation Analysis  
- **Part 2:** Django Application 
- **Part 3:** Daily Automation (cron / cloud trigger)  
- **Part 4:** Documentation (this README)

🎯 Ready for review and testing by the Kipps AI Internship Team.
