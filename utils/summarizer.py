import re
from dataclasses import dataclass
from typing import List, Optional, Tuple
from google import genai

@dataclass
class SummarizeConfig:
    model: str
    mode: str
    length: str
    include_citations: bool = False

LENGTH_RULES = {
    "Short": "Be brief (~5-8 bullets / short sections).",
    "Medium": "Balanced (~10-15 bullets / medium sections).",
    "Long": "Detailed but concise.",
}

MODE_RULES = {
    "Bullets": "Return a clean bullet list of key points.",
    "Key Takeaways": "Return 5–10 key takeaways with short explanations.",
    "Action Items": "Return action items as a checklist. If none, say 'No explicit action items found'.",
    "Study Notes": "Return structured study notes with headings + definitions.",
    "Flashcards": "Return 8–15 flashcards as Q: ... / A: ... pairs.",
}

def chunk_text(text: str, max_chars: int = 9000, overlap: int = 500) -> List[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        start = max(0, end - overlap)
        if end == len(text):
            break
    return chunks

def build_prompt(content: str, cfg: SummarizeConfig, page_hint: Optional[str] = None) -> str:
    cite = ""
    if cfg.include_citations and page_hint:
        cite = f"\nAdd page citations like (p. 3) when relevant. This chunk covers {page_hint}.\n"
    return f"""
Summarize the NOTES below.

MODE: {cfg.mode}
- {MODE_RULES[cfg.mode]}

LENGTH: {cfg.length}
- {LENGTH_RULES[cfg.length]}

Rules:
- Do NOT invent facts.
- If missing, say "Not specified in notes."
{cite}

NOTES:
{content}
""".strip()

def call_llm(client: genai.Client, model: str, prompt: str) -> str:
    resp = client.models.generate_content(model=model, contents=prompt)
    return (resp.text or "").strip()

def summarize(client: genai.Client, text: str, cfg: SummarizeConfig,
              pages: Optional[List[Tuple[int, str]]] = None) -> str:
    if not text.strip():
        return "No text found to summarize."

    # PDF citations path
    if pages and cfg.include_citations:
        partials = []
        cur, cur_chars = [], 0
        start_p, end_p = None, None

        for pno, ptxt in pages:
            ptxt = (ptxt or "").strip()
            if not ptxt:
                continue
            if start_p is None:
                start_p = pno
            end_p = pno

            if cur_chars + len(ptxt) > 9000 and cur:
                hint = f"pages {start_p}–{end_p}"
                partials.append(call_llm(client, cfg.model, build_prompt("\n\n".join(cur), cfg, hint)))
                cur, cur_chars = [], 0
                start_p = pno

            cur.append(ptxt)
            cur_chars += len(ptxt)

        if cur:
            hint = f"pages {start_p}–{end_p}"
            partials.append(call_llm(client, cfg.model, build_prompt("\n\n".join(cur), cfg, hint)))

        if len(partials) == 1:
            return partials[0]

        synth = f"""
Combine these chunk summaries into ONE final output in MODE={cfg.mode} and LENGTH={cfg.length}.
Remove duplicates. Keep citations like (p. 4).

CHUNK SUMMARIES:
{chr(10).join(partials)}
""".strip()
        return call_llm(client, cfg.model, synth)

    # Non-citation path
    chunks = chunk_text(text)
    partials = [call_llm(client, cfg.model, build_prompt(ch, cfg)) for ch in chunks]
    if len(partials) == 1:
        return partials[0]

    synth = f"""
Combine these chunk summaries into ONE final output in MODE={cfg.mode} and LENGTH={cfg.length}.
Remove duplicates.

CHUNK SUMMARIES:
{chr(10).join(partials)}
""".strip()
    return call_llm(client, cfg.model, synth)
