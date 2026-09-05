# AI PPT Generator — Roadmap

An application that takes a topic/prompt (and optional source content) and generates a
polished PowerPoint (.pptx) presentation using AI for content generation and
templated/design logic for layout and styling.

## Goals
- User provides a topic, outline, or source document (text/PDF/URL).
- AI generates slide-by-slide content: titles, bullet points, speaker notes.
- App renders content into a styled .pptx file the user can download and edit.
- Support themes/templates, image suggestions, and export.

## Tech Stack (proposed)
- **Backend**: Python (FastAPI) — good ecosystem for AI + pptx generation
  - `python-pptx` for building slides
  - LLM API (Claude/OpenAI) for content generation
- **Frontend**: React (Vite) or simple server-rendered UI for MVP
- **Storage**: Local/temp file storage for generated decks (S3-compatible later)
- **Auth**: Optional for MVP; add for multi-user/saved decks later

## Phase 0 — Project Setup
- [ ] Initialize repo structure: `backend/`, `frontend/`, `docs/`
- [ ] Set up backend framework (FastAPI) with health-check endpoint
- [ ] Set up dependency management (requirements.txt / pyproject.toml)
- [ ] Add `.gitignore`, basic CI (lint + test) workflow
- [ ] Decide on LLM provider and add API key config via env vars

## Phase 1 — Core Generation Pipeline (MVP)
- [ ] Define input schema: topic, number of slides, tone, audience
- [ ] Prompt design: LLM outputs structured JSON (slide title, bullets, notes)
- [ ] Implement `python-pptx` renderer: JSON → .pptx file
- [ ] Single default template/theme
- [ ] CLI or simple API endpoint: `POST /generate` → returns .pptx file
- [ ] Basic error handling (invalid input, LLM failures, timeouts)

## Phase 2 — Usable Web App
- [ ] Frontend form: topic input, slide count, tone/style selector
- [ ] Progress/loading state while generation runs
- [ ] Preview generated slides (thumbnails or text preview) before download
- [ ] Download generated .pptx
- [ ] Basic input validation and rate limiting

## Phase 3 — Design & Templates
- [ ] Multiple theme options (color palettes, fonts, layouts)
- [ ] Layout variety: title slide, bullet slide, image+text, comparison, quote, section divider
- [ ] Auto image suggestions (stock/AI-generated) inserted into relevant slides
- [ ] Support custom brand templates (upload logo/colors)

## Phase 4 — Content Enhancements
- [ ] Generate from source material: paste text, upload PDF/DOCX, or URL summarization
- [ ] Speaker notes generation
- [ ] Slide count/content regeneration ("regenerate this slide")
- [ ] Tone/style controls (formal, casual, technical, executive summary)
- [ ] Multi-language support

## Phase 5 — Accounts & Persistence
- [ ] User accounts / auth
- [ ] Save/list/edit past generated decks
- [ ] Deck versioning (regenerate without losing history)
- [ ] Sharing/export links

## Phase 6 — Polish & Scale
- [ ] Async job queue for generation (avoid blocking requests)
- [ ] Caching of LLM responses where sensible
- [ ] Usage limits / cost controls for LLM calls
- [ ] Deployment (Docker, CI/CD, hosting)
- [ ] Monitoring/logging and error tracking

## Open Questions
- Which LLM provider(s) to support (Claude, OpenAI, both)?
- Should we support editing the deck in-browser, or is download-and-edit-in-PowerPoint enough for MVP?
- Do we need image generation, or just stock photo search/embedding?
- Single-tenant tool vs. multi-user SaaS from the start?
