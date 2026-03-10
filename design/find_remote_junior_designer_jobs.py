"""Simple agentic browser script to search for remote junior designer jobs.

Requirements (install via uv/pip):
    uv add browser-use playwright
    playwright install

This script is intentionally simple: it opens Indeed, runs a search
for remote junior designer roles, and lets the agent decide how to
navigate and extract results.

Run with:
    python design/find_remote_junior_designer_jobs.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


# NOTE: these imports assume `browser_use` is installed in your env.
# We let any ImportError surface directly so it's clear what's missing.
from browser_use import Agent, BrowserSession, ChatOpenAI  # type: ignore
from browser_use.agent.views import AgentHistoryList  # type: ignore


# Adjust this to match how your LLM client is configured.
# For many browser_use examples, you pass a model name string; for others
# you may need to construct a client. This keeps it simple and
# OpenAI-compatible.
DEFAULT_MODEL = "gpt-4.1-mini"


@dataclass
class JobSearchConfig:
    """Configuration for the job search agent."""

    model: str = DEFAULT_MODEL
    max_steps: int = 40
    # Run the browser in headless mode by default so it works cleanly
    # in non-GUI environments.
    headless: bool = True


def build_prompt() -> str:
    """Return a focused, high-quality AI prompt for the agent.

    The prompt is written for an agentic browser that can click, type,
    scroll, and read page content. Keep it goal-oriented and concrete.
    """

    return (
        "You are an experienced career research assistant using a real web browser.\n\n"
        "Goal: Find high-quality *remote* junior or entry-level design roles, such as "
        "Junior Product Designer, Junior UX Designer, Junior Visual/Graphic Designer, "
        "or similar. Focus on positions that are:\n"
        "- fully remote or remote-first\n"
        "- suitable for candidates with 0–3 years of experience\n\n"
        "Use a well-known job site (for example, Indeed or LinkedIn).\n\n"
        "Browsing strategy:\n"
        "1. Navigate to a major job board.\n"
        "2. Search for remote junior designer roles in English.\n"
        "3. Apply filters for remote/anywhere and junior/entry-level if available.\n"
        "4. Open a few of the most relevant listings in new tabs or navigate into them.\n"
        "5. For each promising role, capture:\n"
        "   - job title\n"
        "   - company name\n"
        "   - location (confirm it is remote)\n"
        "   - seniority or experience level (if stated)\n"
        "   - application URL\n"
        "   - a short plain-text summary of the key requirements (experience, skills, tools)\n\n"
        "Output format:\n"
        "1) First, provide a concise Markdown section titled 'Remote Junior Designer Roles' "
        "where each bullet contains the fields above in a readable way.\n"
        "2) Then, at the very end of your answer, output a single JSON array, inside a "
        "fenced ```json block, with one object per job using EXACTLY this schema:\n"
        "[\n"
        "  {\n"
        "    \"title\": \"...\",\n"
        "    \"company\": \"...\",\n"
        "    \"location\": \"...\",\n"
        "    \"seniority\": \"...\",\n"
        "    \"url\": \"https://...\",\n"
        "    \"requirements\": \"short one-paragraph summary of requirements\"\n"
        "  }\n"
        "]\n"
        "- Use an empty string \"\" for any unknown field.\n"
        "- Do NOT add any other keys to the objects.\n"
        "- Do NOT wrap the JSON array in extra text; the ```json block should contain "
        "ONLY the array.\n\n"
        "Be deliberate and avoid getting stuck on login walls or captchas. If a site "
        "blocks you, switch to another job board."
    )


def _extract_jobs_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract a JSON job list from the agent's final text output.

    Looks for a ```json fenced block containing a top-level array.
    Returns an empty list if parsing fails.
    """

    import json

    # Find the last ```json fenced block and grab the array inside.
    fence = "```json"
    start = text.rfind(fence)
    if start == -1:
        return []

    # Find the opening bracket of the array after the fence.
    bracket_start = text.find("[", start)
    if bracket_start == -1:
        return []

    end_fence = text.find("```", bracket_start)
    if end_fence == -1:
        return []

    json_str = text[bracket_start:end_fence].strip()
    try:
        data = json.loads(json_str)
    except Exception:
        return []

    if not isinstance(data, list):
        return []

    jobs: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        jobs.append(
            {
                "title": str(item.get("title", "")),
                "company": str(item.get("company", "")),
                "location": str(item.get("location", "")),
                "seniority": str(item.get("seniority", "")),
                "url": str(item.get("url", "")),
                "requirements": str(item.get("requirements", "")),
            }
        )
    return jobs


def _render_jobs_markdown(jobs: Iterable[Dict[str, Any]]) -> str:
    """Render a clean Markdown document focused on URLs and requirements."""

    jobs_list = list(jobs)
    if not jobs_list:
        return (
            "# Remote Junior Designer Roles\n\n"
            "No suitable jobs were found in this run.\n"
        )

    lines: List[str] = [
        "# Remote Junior Designer Roles",
        "",
        f"Total roles: {len(jobs_list)}",
        "",
    ]

    for idx, job in enumerate(jobs_list, start=1):
        title = job.get("title", "") or "Unknown title"
        company = job.get("company", "") or "Unknown company"
        location = job.get("location", "") or ""
        seniority = job.get("seniority", "") or ""
        url = job.get("url", "") or ""
        requirements = job.get("requirements", "") or "No requirements summary available."

        lines.append(f"## {idx}. {title}")
        lines.append("")
        lines.append(f"- **Company**: {company}")
        if location:
            lines.append(f"- **Location**: {location}")
        if seniority:
            lines.append(f"- **Seniority**: {seniority}")
        if url:
            lines.append(f"- **URL**: {url}")
        lines.append("")
        lines.append("**Requirements (summary)**:")
        lines.append("")
        lines.append(requirements.strip())
        lines.append("")

    return "\n".join(lines)


async def main(config: JobSearchConfig | None = None) -> None:
    """Run a simple browser-use agent to search for jobs."""

    cfg = config or JobSearchConfig()

    goal = build_prompt()

    print("Starting agentic job search for remote junior designer roles...\n")

    # Configure LLM and browser session for the agent.
    llm = ChatOpenAI(model=cfg.model)
    browser_session = BrowserSession(is_local=True, headless=cfg.headless)

    agent = Agent(task=goal, llm=llm, browser_session=browser_session)

    history: AgentHistoryList = await agent.run(max_steps=cfg.max_steps)

    # Convert the result to text for saving.
    # Prefer the agent's final textual result (markdown + JSON), if present.
    final_text = history.final_result()
    if isinstance(final_text, str) and final_text.strip():
        text_result = final_text
    else:
        text_result = history.json(indent=2)

    # Try to extract a structured job list from the final result text.
    jobs = _extract_jobs_from_text(text_result)
    jobs_markdown = _render_jobs_markdown(jobs)

    # Ensure results directory exists next to this script.
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"remote_junior_designer_jobs_{timestamp}.md"
    output_path.write_text(jobs_markdown, encoding="utf-8")

    print("\n=== Agent Result (jobs summary saved to disk) ===\n")
    print(jobs_markdown)
    print(f"\nSaved job list (URLs and requirements) to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
