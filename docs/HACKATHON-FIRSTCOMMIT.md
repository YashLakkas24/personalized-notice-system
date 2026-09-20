# CampusNotice.AI @ FirstCommit

This document covers what's specific to CampusNotice.AI's submission to **FirstCommit** ("Beginner's Paradise"). For the project itself, see the [main README](../README.md).

## Why this project for FirstCommit

FirstCommit judges on Learning & Growth, Creativity, Execution, Technical Understanding, and Presentation — not on polish or production scale. Here's how CampusNotice.AI maps to that:

**Learning & Growth** — This project meant working across the full stack for real: FastAPI backend design, React state management, OCR pipelines, semantic embeddings, agent-based AI workflows with the Strands Agents SDK, session-based authentication, and background task processing. Several of these (agentic AI workflows, OCR fallback chains, embedding-based matching) were new territory going in.

**Creativity** — Personalized notice routing isn't a novel *problem*, but the approach — splitting "what does this mean" (AI) from "should this student see it" (deterministic logic) — is a deliberate answer to a real failure mode: letting an LLM make institutional eligibility calls is unpredictable and hard to explain when it's wrong. That split is the actual creative decision here, not the surface-level pitch.

**Execution** — The full loop works end to end: an admin uploads a real PDF or image notice, it gets OCR'd and understood by an LLM agent, converted to embeddings, evaluated against real student eligibility and preference data, and routed into a personalized feed a student can actually log in and see — with a visible reason for each recommendation.

**Technical Understanding** — See the main README's "How the AI Actually Works" section for the core architectural reasoning: why the LLM only understands and never decides, and what that buys in predictability and explainability.

**Presentation** — The demo flow in the main README (admin uploads → AI understands → student sees a personalized, explained feed) is designed to be walkable in the 3–5 minute window FirstCommit asks for.

## FirstCommit submission checklist

- [ ] Working project (this repo)
- [ ] Public GitHub repository
- [ ] Project description (what it does, the problem, who it's for) — draft below
- [ ] 3–5 minute demo video
- [ ] README with setup instructions — see main [README.md](../README.md)
- [ ] Screenshots
- [ ] AI assistance disclosure — see main README's disclosure section

## Devpost project description draft

> **CampusNotice.AI** solves the problem of college notice overload: students miss relevant opportunities buried in a flood of announcements, while admins have no way to know who actually needed to see what they published. It's built for any student who's ever missed a deadline because it was one notice among fifty they never read.
>
> The system uses a Strands Agents SDK agent to understand unstructured notices (PDF, image, or text) and extract structured metadata, then uses embeddings to semantically match notices against each student's natural-language interests. Critically, the AI never makes the final call on who gets notified — that decision goes through deterministic eligibility and routing logic, so the system stays predictable and explainable even when the model's understanding of a notice is imperfect.

Feel free to trim or extend this for the actual Devpost form.

## Team

Submitted to FirstCommit by the CampusNotice.AI team.
