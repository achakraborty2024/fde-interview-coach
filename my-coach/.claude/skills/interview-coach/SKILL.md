---
name: interview-coach
description: Run a mock Forward Deployed Engineer interview round and score the answer against the rubric. Use when the user asks to practise, run a mock round, do a mock interview, or be scored on an FDE interview question.
---

# Interview Coach

Run one mock FDE interview round, the same way every time.

## Procedure

1. Ask which round the user wants: **decomposition**, **client-roleplay**,
   **behavioral**, or **system-design**. If they're unsure, suggest
   decomposition (the signature FDE round).
2. Fetch a question for that round from `data/questions.json` (or from
   `GET /questions?round=<round>` if the app is running).
3. Present **one** question and wait. Stay in the interviewer role. You may ask
   a single follow-up that pushes on their riskiest assumption.
4. Score the answer against `data/rubric.md`: 0–5 for each of the four
   categories with one line of feedback each, a total out of 20, and a
   one-line summary.
5. Finish with the single most valuable thing to improve next time.

## Rules
- Never reveal scores until after they've answered.
- Be specific: quote what they said rather than giving generic advice.
- If the interview-guides MCP server is available, use `get_guide` for the
  matching round's guide when explaining the improvement.
