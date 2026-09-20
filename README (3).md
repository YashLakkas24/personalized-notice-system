# CampusNotice.AI

### Personalized college notice intelligence

> One notice for the administration. The right information for every student.

CampusNotice.AI turns a traditional college notice board into a personalized information system. Instead of every student manually scanning dozens of announcements, the system understands each incoming notice, checks academic eligibility, matches it against each student's stated interests, and surfaces only what's actually relevant — with a visible reason why.

<!--
SCREENSHOT: Student "Relevant to You" feed, with at least one notice card
expanded to show its "why this was recommended" reason text.
This is the single most important image in this README — it's the
one piece of evidence that personalization is real and not just a
claim. Replace this comment block with:
![Relevant to You feed](docs/screenshots/relevant-to-you.png)
-->

<!--
DEMO VIDEO: 3–5 minute walkthrough covering the flow in "Demo Flow" below.
Replace this comment with a link once recorded, e.g.:
📺 [Watch the demo](https://your-video-link)
-->

---

## The Problem

Colleges publish a large number of notices every week — workshops, hackathons, competitions, club activity, placement opportunities, academic announcements, registration deadlines. The problem isn't a lack of information; it's **information overload**. Students receive notices irrelevant to them while missing ones that genuinely match their interests. Administrators face the mirror problem: after publishing a notice, there's no good way to know who actually needed to see it.

```text
Administrator
     │
     ▼
Publish notice
     │
     ▼
Broadcast to everyone
     │
     ▼
Students manually search
     │
     ▼
Relevant notices get missed
```

## The Solution

CampusNotice.AI replaces "broadcast everything to everyone" with a pipeline that understands each notice once and routes it individually.

```text
Administrator
     │
     ▼
Upload or paste a notice
     │
     ▼
Text extraction / OCR
     │
     ▼
Strands Agent understands the notice
     │
     ▼
Structured notice metadata
     │
     ▼
Semantic embedding
     │
     ▼
Eligibility + relevance evaluation
     │
     ▼
Decision + priority
     │
     ▼
Personalized student notification
```

The administrator publishes a notice once. Everything downstream — understanding, matching, routing — happens automatically.

---

## How the AI Actually Works

CampusNotice.AI deliberately separates **understanding** from **deciding**. This is the core engineering decision behind the project.

**1. Strands Agent — understanding a notice.** Answers *"what does this notice mean?"* It turns unstructured notice text (a PDF, a photo of a poster, pasted text) into structured metadata: category, summary, deadline, eligibility criteria as stated in the notice, mandatory status, registration link.

**2. A second LLM call — understanding a student's preferences.** Before a student's natural-language preferences are embedded, a separate lightweight model call splits a sentence like *"I like football and technical workshops"* into distinct interest groups (football-related terms, technical-workshop-related terms) and expands each one moderately. This is a real, separate use of the LLM — not the same call as notice understanding, and worth naming explicitly since it's easy to miss reading the pipeline diagram alone.

**3. Embeddings — relevance.** Answers *"how semantically related is this notice to what this student cares about?"* Both the notice and each of the student's expanded interest groups are converted to embeddings; a notice is matched against whichever group scores highest, so related concepts match even when the wording differs (a student who wrote "robotics" can still match a notice about an "autonomous systems workshop").

**4. Deterministic engines — the decision.** Answers *"is this student eligible, and should they actually be notified?"* Eligibility (year, branch), the notify/suppress decision, and priority are all plain application logic — not the LLM.

**Why split it this way?** An LLM is genuinely good at extracting meaning from messy, inconsistent text — that's real, hard-to-fake work. But institutional decisions like "does this student meet the eligibility requirement" benefit from logic that's predictable, testable, and explainable without needing to re-run a model. The LLM is never the final authority on whether a student gets notified.

### Worked example

A student sets their preferences to:

```text
I am interested in football, technical workshops and robotics.
```

Four notices exist: a football tournament, an AI/ML workshop, a robotics club recruitment drive, and a first-year-only orientation. The system doesn't keyword-match — it runs each notice through eligibility and relevance separately:

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

If this student is in their third year, the first-year-only orientation is filtered out by eligibility even though nothing about its *topic* is irrelevant to them. That distinction — relevance vs. eligibility — is a deliberate design choice, not an accident of how embeddings happen to score things.

---

## Key Features

**AI notice understanding** — Admins provide notices as PDF, image, TXT, or pasted text. A Strands Agent extracts title, category, summary, importance, mandatory status, eligibility, deadline, required action, and registration link.

**Personalized student feed** — Combines academic eligibility, natural-language preferences, semantic similarity, and notice priority into a single "Relevant to You" feed per student.

**Natural-language preferences** — Students describe interests in plain language rather than picking from a fixed tag list; the system captures related concepts, not just exact words.

**All Notices** — Personalization doesn't remove transparency. Students can always view the full published notice list, not just their filtered feed.

**Student profile** — Students see their own academic info (ID, name, year, branch); their preference data stays private and separate from what the admin sees.

**Admin portal** — Create student profiles, upload single or multiple notices, paste raw text, and view notice processing history. Admins do not see which individual students received which notices.

---

## System Architecture

The pipeline above shows the *conceptual* flow. In terms of actual backend components, one notice moves through:

```text
Notice Ingestion (PDF / image / text)
  → Text Extraction / OCR
  → Strands Agent (understanding)
  → Structured Notice Metadata
      ├─ stored in Notice Database
      └─ converted to a Notice Embedding
            → compared against Student Preference Embeddings   (Semantic Relevance)
            → checked against Student Academic Profile          (Eligibility Engine)
                  → Decision Engine → Priority Engine → Notification Service
                        → surfaced in the Student Portal (Relevant to You / All Notices / My Profile / My Preferences)
```

### Main components

| Component | Responsibility |
|---|---|
| **Strands Agent** | Understands unstructured college notices |
| **Embedding Service** | Creates semantic representations |
| **Eligibility Engine** | Evaluates academic eligibility (year, branch) |
| **Decision Engine** | Determines whether a notification should be created |
| **Priority Engine** | Determines notification priority |
| **Notification Service** | Creates and deduplicates student notifications |
| **PostgreSQL** | Stores students, notices, and notifications |
| **FastAPI** | Backend API and orchestration |
| **React** | Admin and student interfaces |

---

## Tech Stack

**Frontend** — React, Vite, JavaScript, CSS

**Backend** — Python, FastAPI, SQLAlchemy

**AI** — Strands Agents SDK, OpenAI (GPT-4o-mini), `text-embedding-3-small`

**Document processing** — pypdf, Tesseract OCR, Pillow, pdf2image

**Database** — PostgreSQL

---

## Project Structure

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
│   │   ├── schemas/
│   │   │   └── notice.py
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
│   ├── uploads/
│   ├── create_tables.py
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
├── docs/
│   └── HACKATHON-FIRSTCOMMIT.md
│
├── README.md
└── LICENSE
```

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js
- PostgreSQL (running, with a database created for this project — e.g. `createdb campusnotice`)
- Tesseract OCR
- Poppler (required by `pdf2image`)

### 1. Clone the repository

```bash
git clone https://github.com/YashLakkas24/personalized-notice-system.git
cd personalized-notice-system
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/campusnotice
TESSERACT_PATH=path_to_tesseract_executable
POPPLER_PATH=path_to_poppler_bin_folder
STUDENT_AUTH_SECRET=any_random_string
```

`TESSERACT_PATH` and `POPPLER_PATH` are only needed if these tools aren't already on your system `PATH`. `STUDENT_AUTH_SECRET` signs student tokens — it has a working default for local testing, but set your own value for anything beyond a quick local run. Never commit a real `.env` file — it's already covered by `.gitignore`.

### 4. Start the backend

From `backend/`:

```bash
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Interactive API docs: `http://127.0.0.1:8000/docs`

Tables are created automatically on startup. If you want to verify the database connection independently, you can also run `python create_tables.py` from `backend/`.

### 5. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL Vite prints in the terminal. The frontend talks to `http://127.0.0.1:8000` by default — only set a `VITE_API_BASE_URL` environment variable if your backend runs somewhere else.

---

## Try It

**Demo student login:**

```text
Student ID: student_1
Password: student123
```

These are shown directly on the login page so anyone can start testing immediately without setting up their own data.

**Suggested flow (as an admin, then as a student):**

1. As admin, create a student profile (or use the demo student above).
2. As admin, paste or upload a notice.
3. Wait a few seconds — notice processing (AI extraction, embedding, routing) runs in the background, not inline, so the response returns before it's fully done.
4. Log in as the student and set their preferences in plain language.
5. Open **Relevant to You** and check for the notice.
6. Open the notice and look at its recommendation reason.
7. Open **All Notices** to see the full, unfiltered list for comparison.

This walks the complete loop: notice ingestion → AI understanding → personalized delivery. Step 3 matters for a live demo — if you check the student feed immediately after uploading, the notice may not have finished processing yet.

---

## Authentication & Privacy

**Student side.** Logging in checks a password against the stored value, and the server returns an HMAC-SHA256-signed token tying that response to one student ID. Every student-scoped endpoint (profile, notifications) verifies the signature and rejects mismatched or missing tokens before returning any data. This is a real, working mechanism, not a stub — but it's intentionally minimal: the token never expires, there's no logout or revocation, passwords are stored in plain text with a shared default (`student123`) for the demo dataset, and the signing secret falls back to a hardcoded value if `STUDENT_AUTH_SECRET` isn't set. Good enough to demonstrate per-student access control; not something to expose beyond a demo without hardening.

**Admin side.** Admin endpoints currently have no authentication at all — anyone with the backend URL can create students or upload notices. This matches the project's stated MVP scope (the focus is the notice-understanding and personalization pipeline, not access control), but it's worth stating plainly rather than leaving a judge to discover it.

**Privacy boundary.** Separately from authentication, the application enforces a data-visibility rule by design: the admin view shows student academic data (ID, name, year, branch) but never individual preferences or which students received which notices.

---

## Challenges

**Unstructured document formats.** Notices arrive as text PDFs, scanned PDFs, images, and plain text. Multiple extraction paths plus an OCR fallback were needed to handle all of them reliably.

**Semantic personalization.** Keyword matching wasn't sufficient for natural-language preferences — a student writing "robotics" should still match "autonomous systems," which keyword search misses. Embeddings solved this, but tuning what counts as "relevant enough" required real testing against actual notices, not just intuition.

**Eligibility vs. relevance.** A notice can be topically interesting to a student without being applicable to them (a first-year-only event to a third-year student). Keeping these as two separate evaluations, rather than one blended score, was necessary to model how college notices actually work.

**Full-stack coordination.** Getting React state, FastAPI endpoints, background AI processing, database persistence, and student-specific data retrieval to work together correctly — especially once notice processing moved to background tasks — required careful attention to what happens when a student loads their feed while a notice is still mid-processing.

**Auth vs. real access control.** Building a login *screen* is easy; making sure every student-scoped request is actually tied to a verified token, and that one student can't read another's data by changing an ID in a request, took more care than the UI alone suggests.

---

## What We Learned

Building this required working across the full stack: FastAPI API design, React state and UI flow, PostgreSQL/SQLAlchemy, OCR and document processing, semantic embeddings, agent-based AI workflows with the Strands Agents SDK, deterministic business-rule design, signed-token authentication, and background processing for slow AI operations.

The biggest lesson: **building an AI application isn't mainly about sending text to a model.** The real engineering work is designing the system *around* the model — deciding what the model should and shouldn't be trusted to decide, how its output gets validated and used by deterministic code, and what happens when it's wrong, slow, or unavailable.

---

## Future Improvements

- Production-grade authentication (password hashing, proper session/refresh handling)
- Push or email notifications instead of in-app only
- Department-level administration and multi-college support
- Notice acknowledgement tracking
- A dedicated vector index for embedding search at scale
- Cloud deployment

---

## AI Assistance Disclosure

AI tools were used during development as learning and development aids — for brainstorming architecture decisions, debugging, explaining unfamiliar concepts, reviewing implementation choices, and refining documentation. The team was responsible for the actual architecture, integration, testing, debugging, and final implementation decisions throughout. AI assistance supported the work; it didn't replace understanding the system being built.

---

## License

MIT — see [`LICENSE`](LICENSE).

## Team

Built by the CampusNotice.AI team.
