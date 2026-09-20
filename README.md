# 🤖 CampusNotice.AI

### AI-powered personalized college notice intelligence

> **One notice for the administration. The right information for every student.**

CampusNotice.AI turns a traditional college notice system into a personalized information platform.

Instead of asking every student to manually search through dozens of announcements, the system understands incoming notices, evaluates academic eligibility, matches notices against student preferences, and surfaces the information that matters to each student.

---

## 🎯 The Problem

Colleges publish a large number of notices every week:

- Workshops
- Hackathons
- Competitions
- Club activities
- Placement opportunities
- Academic announcements
- Events
- Registration opportunities

The problem is not a lack of information. It is **information overload**.

A student may receive many notices that are irrelevant to them while missing opportunities that match their interests.

Administrators also face the opposite problem: after publishing a notice, they may need to manually identify and distribute it to the relevant student groups.

### Traditional workflow

```text
Administrator
     ↓
Publish notice
     ↓
Send to everyone
     ↓
Students manually search
     ↓
Relevant information can be missed
```

---

# 💡 Our Solution

CampusNotice.AI changes the workflow from broadcasting everything to everyone into an automated personalization pipeline.

```text
Administrator
     ↓
Upload / paste notice
     ↓
Text extraction / OCR
     ↓
Strands Agent understands notice
     ↓
Structured notice metadata
     ↓
Semantic embedding
     ↓
Eligibility + relevance evaluation
     ↓
Decision + priority
     ↓
Personalized student notification
```

The administrator publishes the notice once. The system handles the downstream analysis and routing.

---

# ✨ Key Features

## 🤖 AI Notice Understanding

Administrators can provide notices as:

- PDF files
- Images
- TXT files
- Raw pasted text

The system extracts the content and uses a **Strands Agent** to transform unstructured notice text into structured information such as:

- Title
- Category
- Summary
- Importance
- Mandatory status
- Eligibility
- Deadline
- Required action
- Registration link

---

## 🎯 Personalized Student Feed

Students do not need to manually scan every announcement.

CampusNotice.AI combines:

- Academic eligibility
- Natural-language student preferences
- Semantic similarity
- Notice priority
- Deadline and urgency information

The result is a **Relevant to You** feed containing notices selected for that student.

---

## 🧠 Natural-Language Preferences

Students describe what they are interested in using normal language.

Example:

```text
I am interested in football competitions,
technical workshops, hackathons and robotics.
```

The system converts the preference into a semantic representation and compares it with the meaning of incoming notices.

This allows the system to capture related concepts rather than relying only on exact keyword matches.

---

## 📋 All Notices

Personalization does not remove transparency.

Students can still open **All Notices** and view the complete published notice collection.

---

## 👤 Student Profile

Students can view their own academic information:

- Student ID
- Name
- Academic year
- Branch

Student preferences are kept separate from the administrator's student-management view.

---

## 🏛️ Admin Portal

Administrators can:

- Create student profiles
- View registered student academic profiles
- Upload a single notice
- Upload multiple notices
- Paste notice text
- Process PDF/image notices
- View notice processing history

Student preferences are intentionally not exposed in the admin student listing.

---

# 🧠 How the AI Works

CampusNotice.AI deliberately separates **AI understanding** from **business decisions**.

### 1. Strands Agent — Understanding

The Strands Agent answers:

> **What does this notice mean?**

Raw notice content is transformed into structured metadata that can be consumed by the rest of the application.

### 2. Embeddings — Semantic Relevance

Embeddings answer:

> **How semantically related is this notice to the student's preferences?**

Student preference text and notice content are represented numerically so their semantic relationship can be evaluated.

### 3. Deterministic Engines — Decisions

Deterministic application logic answers:

> **Should this student actually receive this notice?**

Eligibility, notification decisions, and priority are handled separately from the LLM.

### Core architectural principle

> **AI understands. Deterministic logic decides.**

This makes the system easier to reason about, test, and explain.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │   Administrator  │
                         └────────┬─────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │  Notice Ingestion  │
                        │ PDF / Image / Text │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │ Text Extraction /  │
                        │       OCR          │
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │   Strands Agent    │
                        │ Notice Understanding│
                        └─────────┬──────────┘
                                  │
                                  ▼
                        ┌────────────────────┐
                        │ Structured Notice  │
                        │     Metadata       │
                        └───────┬─────┬──────┘
                                │     │
                 ┌──────────────┘     └──────────────┐
                 ▼                                   ▼
        ┌──────────────────┐                 ┌─────────────────┐
        │ Notice Embedding │                 │ Notice Database │
        └────────┬─────────┘                 └─────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ Semantic Relevance│◄──────── Student Preferences
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │ Eligibility Engine │◄──────── Student Academic Profile
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │   Decision Engine  │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │   Priority Engine  │
        └─────────┬──────────┘
                  │
                  ▼
        ┌────────────────────┐
        │Notification Service│
        └─────────┬──────────┘
                  │
                  ▼
          ┌─────────────────┐
          │ Student Portal  │
          ├─────────────────┤
          │ Relevant to You │
          │ All Notices     │
          │ My Profile      │
          │ My Preferences  │
          └─────────────────┘
```

---

# 🔄 End-to-End Workflow

## Step 1 — Notice ingestion

The administrator uploads or pastes a college notice.

## Step 2 — Text extraction

- Text-based PDFs use direct extraction.
- Scanned PDFs can fall back to OCR.
- Images are processed with OCR.
- TXT files are decoded directly.

## Step 3 — AI understanding

The notice is passed to the Strands Agent, which extracts structured notice metadata.

## Step 4 — Semantic representation

The notice is converted into an embedding.

## Step 5 — Eligibility filtering

The system evaluates whether a student is academically eligible based on information such as:

- Year
- Branch
- Notice eligibility requirements

## Step 6 — Relevance matching

The student's natural-language preferences are compared semantically with the notice.

## Step 7 — Notification decision

The decision and priority layers determine whether a notification should be created and how it should be surfaced.

## Step 8 — Personalized delivery

The student sees the resulting notification in **Relevant to You**.

---

# 🧩 Main Components

| Component | Responsibility |
|---|---|
| **Strands Agent** | Understands unstructured college notices |
| **Embedding Service** | Creates semantic representations |
| **Eligibility Engine** | Evaluates academic eligibility |
| **Decision Engine** | Determines notification decisions |
| **Priority Engine** | Determines notification priority |
| **Notification Service** | Creates student notifications |
| **PostgreSQL** | Stores students, notices and notifications |
| **FastAPI** | Backend API and application orchestration |
| **React** | Admin and student interfaces |

---

# 🧪 Example

Suppose a student enters:

```text
I am interested in football,
technical workshops and robotics.
```

The system receives these notices:

```text
1. Football Tournament
2. AI & ML Workshop
3. Robotics Club Recruitment
4. First Year Orientation
```

The system does not simply search for matching words.

It evaluates each notice through the workflow:

```text
                 Notice
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 Academic Eligibility     Semantic Relevance
        │                       │
        └───────────┬───────────┘
                    ▼
             Decision Engine
                    │
                    ▼
              Priority Engine
                    │
                    ▼
             Student Feed
```

For a third-year student, a first-year-only notice can be filtered out even if its general topic is relevant.

That distinction between **relevance** and **eligibility** is a core design decision in CampusNotice.AI.

---

# 🔐 Authentication & Privacy

The student portal uses a lightweight authentication/session flow appropriate for the hackathon MVP.

Student-specific endpoints validate the authenticated student context before returning or modifying student-scoped information.

The application also separates:

### Admin-visible student information

- Student ID
- Name
- Academic year
- Branch

### Student-private information

- Personal notice preferences
- Preference embeddings / personalization data

The project is intentionally scoped as a hackathon MVP rather than a production identity-management platform.

---

# 🛠️ Tech Stack

## Frontend

- React
- Vite
- JavaScript
- CSS

## Backend

- Python
- FastAPI
- SQLAlchemy

## AI

- Strands Agents SDK
- OpenAI
- GPT-4o-mini
- `text-embedding-3-small`

## Document Processing

- PyPDF
- Tesseract OCR
- Pillow
- PDF-to-image conversion

## Database

- PostgreSQL

---

# 📁 Project Structure

```text
personalized-notice-system/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── notice_agent.py
│   │   │   └── prompts.py
│   │   │
│   │   ├── models/
│   │   │   ├── student.py
│   │   │   ├── notice.py
│   │   │   └── notification.py
│   │   │
│   │   ├── services/
│   │   │   ├── notice_workflow.py
│   │   │   ├── eligibility_engine.py
│   │   │   ├── decision_engine.py
│   │   │   ├── priority_engine.py
│   │   │   ├── notification_service.py
│   │   │   └── embedding_service.py
│   │   │
│   │   ├── database.py
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── uploads/
├── README.md
└── LICENSE
```

---

# ⚙️ Setup

## Prerequisites

Install the following:

- Python 3.11+
- Node.js
- PostgreSQL
- Tesseract OCR
- Poppler

---

## 1. Clone the repository

```bash
git clone https://github.com/YashLakkas24/personalized-notice-system.git
cd personalized-notice-system
```

---

## 2. Backend setup

```bash
cd backend
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Configure environment variables

Create:

```text
backend/.env
```

Example:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_postgresql_connection_string
TESSERACT_PATH=path_to_tesseract
POPPLER_PATH=path_to_poppler
```

Never commit real API keys or credentials to GitHub.

---

## 4. Start the backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 5. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local Vite URL shown in the terminal.

---

# 🎓 Demo Access

For the hackathon demo:

```text
Student ID: student_1
Password: student123
```

The credentials are intentionally displayed on the Student Login page so judges can start testing immediately.

---

# 🧪 Recommended Demo Flow

## Administrator

```text
Admin Portal
     ↓
Create student profiles
     ↓
Upload / paste notices
     ↓
AI understands notices
     ↓
System evaluates eligibility + relevance
     ↓
Notifications are created
```

## Student

```text
Student Login
     ↓
Set natural-language preferences
     ↓
Relevant to You
     ↓
Open a recommended notice
     ↓
See why it was recommended
     ↓
Check All Notices
```

This flow demonstrates the complete product loop from **notice ingestion → AI understanding → personalization → student delivery**.

---

# 🧠 Why We Didn't Let the LLM Decide Everything

A major technical decision was to avoid using the LLM as the final authority for every business decision.

An LLM is useful for interpreting unstructured notice language, but institutional routing decisions benefit from deterministic logic.

Therefore, the architecture is:

```text
Unstructured Notice
        ↓
    Strands Agent
        ↓
 Structured Meaning
        ↓
Deterministic Engines
        ↓
Student Notification
```

This separation improves predictability, explainability, and debugging.

---

# 🧱 Challenges We Faced

## Unstructured document formats

College notices may arrive as text PDFs, scanned PDFs, images, or plain text.

We therefore built multiple extraction paths and an OCR fallback for scanned content.

## Semantic personalization

Keyword matching was not sufficient for natural-language preferences.

We used embeddings so semantically related concepts could be matched even when the exact wording differs.

## Eligibility vs relevance

A notice can be interesting to a student without being applicable to that student.

Separating the two concepts allowed us to model the actual college workflow more accurately.

## Frontend/backend integration

The project required coordinating React state, FastAPI endpoints, asynchronous notice processing, database persistence, and student-specific notification retrieval.

This made debugging the complete pipeline an important part of the development process.

## Authentication and privacy

We also had to distinguish between a login interface and actual access control, making sure student-specific requests are tied to the authenticated student context and that private preference information is not exposed through the administrator interface.

---

# 📚 What We Learned

Building CampusNotice.AI required learning across the full application stack.

We worked with:

- Full-stack application architecture
- FastAPI API design
- React state and UI flows
- PostgreSQL and SQLAlchemy
- OCR and document processing
- Semantic embeddings
- Agent-based AI workflows
- Strands Agents SDK
- Deterministic business rules
- Authentication and access control
- Frontend/backend debugging
- Background processing of expensive AI operations

One of the biggest lessons was that building an AI application is not simply about sending text to an LLM.

The engineering challenge is designing the system around the model so that AI output can be used reliably by the rest of the application.

---

# 🚀 Future Improvements

Potential future improvements include:

- AWS-native deployment
- Amazon Bedrock model integration
- Production-grade authentication
- Push notifications
- Email / messaging integrations
- Department-level administration
- Notice acknowledgement tracking
- Advanced analytics
- Dedicated vector database infrastructure
- Multi-college support

---

# 🤖 AI Assistance Disclosure

AI tools were used during development as learning and development assistants.

They were used for activities such as:

- Brainstorming and architecture discussions
- Debugging
- Understanding unfamiliar concepts
- Reviewing implementation decisions
- Refining parts of the code
- Improving documentation

The project team remained responsible for the architecture, integration, testing, debugging, and final implementation decisions.

AI was used as a development aid rather than as a substitute for understanding the system.

---

# 🏆 Built for FirstCommit

CampusNotice.AI was built for the **FirstCommit** hackathon.

The project focuses on:

- **Learning & Growth** — exploring agentic AI, full-stack development, OCR, embeddings, authentication, and system design.
- **Creativity** — applying AI personalization to a familiar but underserved college workflow.
- **Execution** — delivering a working end-to-end system from notice ingestion to personalized student notifications.
- **Technical Understanding** — deliberately separating AI understanding from deterministic business decisions.
- **Presentation** — making the complete workflow simple for both administrators and students to demonstrate.

---

# 📜 License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.

---

# 👨‍💻 Team

Built for **FirstCommit** by the CampusNotice.AI team.

---

## ⭐ Our Goal

> **AI understands. Students discover. Nothing gets missed.**
