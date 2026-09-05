# AI PPT Generator — Roadmap

An app that turns text/PDFs/instructions into a polished PowerPoint (.pptx),
built incrementally so each layer of complexity is understood before adding the next.

## Final Architecture
```
User
 -> Streamlit (UI: input, questions, outline review, download)
 -> FastAPI (backend/API layer)                         [Phase 7]
 -> LangGraph (agentic workflow: plan/clarify/generate/review)  [Phase 3+]
 -> Groq (LLM calls)
 -> RAG / FAISS (only when large docs actually need it)  [Phase 6, if justified]
 -> python-pptx (renders the final slide plan)
 -> Generated .pptx
```
No technology is added before it's needed. Simple working app first, complexity only when justified.

## Content Requirements (apply from Phase 2 onward, refined over time)
- Content comes primarily from the user's uploaded PDFs, text, and instructions — never invented.
- The AI decides the presentation structure (which sections to include) based on content,
  purpose, and audience. No fixed slide count/template. Typical candidate sections (used only
  when relevant): Title, Introduction/Overview, Background, Problem Statement, Objectives,
  Current Situation/Challenges, Proposed Solution, Key Features/Approach, Process/Workflow,
  Technical Architecture, Implementation/Methodology, Data/Results/Findings, Charts/Tables,
  Benefits/Business Impact, Challenges/Limitations, Future Scope/Recommendations, Conclusion,
  References/Sources.
- Slide quality: clear titles, concise bullets (no big paragraphs), highlight key numbers,
  use tables/charts when they help, logical flow, appropriate for the stated audience.
- Factual accuracy: never invent facts/stats/names/dates. If something important is missing,
  ask a clarification question. Respect "let AI decide" and "skip" responses.
- User-controllable options (all optional): purpose, audience, slide count, topics to
  focus on/exclude, level of detail, presentation style, chart type, chart colors,
  speaker notes on/off, sources on/off, use previous PPT as visual reference.
  Natural-language instructions ("make this 10 slides for a client", "focus on results",
  "keep it simple", "use charts for the results") should also be understood and applied.
- Outline-first flow: AI proposes an outline before generating the deck. User can add,
  remove, rename, reorder, or combine slides, or change focus, before approving.
- Speaker notes (when enabled): keep slide text concise, put elaboration in notes.
- Source tracking (when practical, especially for PDFs): e.g. "Source: Project_Report.pdf — Page 12",
  to improve reliability and reduce hallucination.

## Phase 1 — Core Loop (DONE)
Text -> Groq (`openai/gpt-oss-120b`) -> structured slide plan (JSON) -> python-pptx -> download.
Plain Streamlit app, single Groq call, no backend split yet.

## Phase 2 — Multiple PDF Uploads (next)
- Upload multiple PDFs + free-text instructions.
- Extract text directly (no RAG yet) and feed into the same Groq call.
- Start applying basic user controls: slide count, focus topics, style/tone.

## Phase 3 — LangGraph Workflow Nodes
- Split the single Groq call into workflow steps: understand input -> plan outline -> generate slides.
- This is where "AI decides the structure" and natural-language instruction parsing live.

## Phase 4 — Human-in-the-Loop
- AI asks only necessary clarification questions when info is missing.
- User can answer, pick an option, let AI decide, or skip.
- Outline-first: user reviews and edits the proposed outline (add/remove/rename/reorder/combine)
  before final generation.
- If the outline includes slides with chart-worthy data and the user hasn't specified a
  chart type/color preference, the AI asks about it here (e.g. "This slide has comparison
  data — bar, line, or pie chart, or let AI decide?") rather than only exposing it as a
  static Phase 8 setting.
- Workflow pauses/resumes using LangGraph state.

## Phase 5 — Slide Quality Check + Revision Loop
- AI reviews its own generated slides for quality/coherence and revises before finalizing.

## Phase 6 — RAG + FAISS (only if justified)
- Added only for large PDFs / many documents / retrieval-heavy needs.
- If introduced, will explain: the problem it solves, why simple extraction stopped being
  enough, how embeddings/FAISS/retrieval work, and how retrieved chunks + page sources
  feed into Groq (enables per-page source tracking).

## Phase 7 — FastAPI Backend Layer
- Restructure to Streamlit -> FastAPI -> LangGraph -> Groq/RAG -> python-pptx.
- Endpoints: generate presentation, process uploaded documents, handle clarification
  responses, get generation status/result.
- Pydantic request/response schemas.

## Phase 8 — Design, Templates, Charts & Reference PPT
- Multiple themes/layouts; charts (bar/line/pie) and tables generated when data fits,
  with user choice of Auto (AI decides) or a specific chart type/colors.
- Speaker notes generation.
- Reference PPT feature: upload a previous .pptx to use as a *style/format* reference only
  (layouts, theme, colors, fonts, title placement, header/footer, logo placement, bullet/table/
  chart styles). Content still comes from the new PDFs/text/instructions, not the old deck,
  unless the user explicitly asks to reuse old content.
  Options: No reference (AI designs) / Use previous PPT as reference / Use company template.
  Optional: upload company logo/brand info alongside the reference PPT.
  Exact format cloning has real technical limits with python-pptx — closest reliable
  approximation will be used, with limitations explained when hit.

## Phase 9 — Deployment
