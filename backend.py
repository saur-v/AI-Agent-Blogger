from __future__ import annotations
import os
import operator
from typing import TypedDict , List , Annotated , Literal , Optional , Dict , Any
from pathlib import Path
from pydantic import BaseModel , Field
from langgraph.graph import StateGraph , START , END
from langgraph.types import Send
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage , HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from datetime import date
from together import Together
import requests
import time

from dotenv import load_dotenv

load_dotenv()


# ===================== DATA MODELS =====================

class Task(BaseModel):
    id: int
    title: str

    goal: str = Field(
        ..., 
        description = "one sentence describing what the reader should be able to do/understand after this section")

    bullets: List[str] = Field(
        ...,
        min_items=3,
        max_items=5,
        description = "3-5 concrete , non overlapping subpoints to cover in this section"
    )   

    target_words: int = Field(
        ...,
        description = "target word count for this section (120-450)."
    )

    tags: List[str] = Field(default_factory=list)
    requires_research: bool = False
    requires_citations: bool = False
    requires_code: bool = False


class Plan(BaseModel):
    blog_title: str
    audience: str = Field(
        ...,
        description = "who this blog is for"
    )
    tone: str = Field(
        ...,
        description = "writing tone , example(practical , crisp)"
    )
    blog_kind: Literal['explainer', 'tutorial', 'news_roundup', 'comparison', 'system_design'] = 'explainer'
    constraints: List[str] = Field(default_factory=list)
    tasks: List[Task]


class EvidenceItem(BaseModel):
    title: str
    url: str
    published_at: Optional[str] = None
    snippet: Optional[str] = None
    source: Optional[str] = None


class RouterDecision(BaseModel):
    needs_research: bool
    mode: Literal["closed_book", "hybrid", "open_book"]
    queries: List[str] = Field(default_factory=list)


class EvidencePack(BaseModel):
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ImageSpec(BaseModel):
    placeholder: str = Field(...,description = "e.g. [[IMAGE_1]]")
    filename: str = Field(...,description = "save under images/ e.g. qkv_flow.png")
    alt: str
    caption: str
    prompt: str = Field(..., description = "prompt to send to the image model")
    size: Literal['1024*1024','768x1408', '1408x768'] = "1024*1024"
    quality: Literal["low","medium","high"] = "medium"


class GlobalImagePlan(BaseModel):
    md_with_placeholders: str
    images: List[ImageSpec] = Field(default_factory=list)


class State(TypedDict):
    topic: str

    plan: Optional[Plan]
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItem]

    as_of: str
    recency_days: int

    sections: Annotated[List[tuple[int, str]], operator.add]

    merged_md: str
    md_with_placeholders: str
    image_specs: List[dict]
    final: str


# ===================== LLM SETUP =====================

llm = ChatOpenAI(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    temperature=0,
    max_tokens=8192,
    openai_api_base="https://api.together.ai/v1"
)


# ===================== ROUTER NODE =====================

ROUTER_SYSTEM = """You are a routing module for a technical blog planner.

Decide whether web research is needed BEFORE planning.

Modes:
- closed_book (needs_research=false):
  Evergreen topics where correctness does not depend on recent facts (concepts, fundamentals).
- hybrid (needs_research=true):
  Mostly evergreen but needs up-to-date examples/tools/models to be useful.
- open_book (needs_research=true):
  Mostly volatile: weekly roundups, "this week", "latest", rankings, pricing, policy/regulation.

If needs_research=true:
- Output 3–10 high-signal queries.
- Queries should be scoped and specific (avoid generic queries like just "AI" or "LLM").
- If user asked for "last week/this week/latest", reflect that constraint IN THE QUERIES.
"""

def router_node(state: State) -> dict:

    topic = state["topic"]
    decider = llm.with_structured_output(RouterDecision)
    decision = decider.invoke(
        [
            SystemMessage(content = ROUTER_SYSTEM),
            HumanMessage(content = f"Topic: {topic}")
        ]
    )

    return {
        "needs_research": decision.needs_research,
        "mode": decision.mode, 
        "queries": decision.queries
    }


def route_next(state: State) -> str:
    return "research" if state["needs_research"] else "orchestrator"


# ===================== RESEARCH NODE =====================

def _tavily_search(query: str , max_results: int = 5) -> List[dict]:
    tool = TavilySearchResults(max_results=max_results)
    results = tool.run(query)
    
    normalized: List[dict] = []
    for r in results or []:
        normalized.append(
            {
                "title": r.get("title") or "",
                "url": r.get("url") or "",
                "snippet": r.get("content") or r.get("snippet") or "",
                "published_at": r.get("published_date") or r.get("published_at") or "",
                "source": r.get("source")
            }
        )

    return normalized



RESEARCH_SYSTEM = """You are a research synthesizer for technical writing.

Given raw web search results, produce a deduplicated list of EvidenceItem objects.

Rules:
- Only include items with a non-empty url.
- Prefer relevant + authoritative sources (company blogs, docs, reputable outlets).
- If a published date is explicitly present in the result payload, keep it as YYYY-MM-DD.
  If missing or unclear, set published_at=null. Do NOT guess.
- Keep snippets short.
- Deduplicate by URL.
"""

def research_node(state: State) -> dict:
    queries = (state.get("queries", []) or [])
    max_results = 2  # Reduce from 6 to 3

    raw_results: List[dict] = []

    for q in queries:
        raw_results.extend(_tavily_search(q, max_results=max_results))

    if not raw_results:
        return {"evidence": []}
    
    extractor = llm.with_structured_output(EvidencePack)
    pack = extractor.invoke([
        SystemMessage(content=RESEARCH_SYSTEM),
        HumanMessage(content=f"Raw results:\n {raw_results[:15]}")  # Limit raw results
    ])

    # Deduplicate by url and limit to top 10
    dedup = {}
    for e in pack.evidence:
        if e.url and len(dedup) < 5:
            dedup[e.url] = e

    return {"evidence": list(dedup.values())}       


# ===================== ORCHESTRATOR NODE =====================

ORCH_SYSTEM = """You are a senior technical writer and developer advocate.
Your job is to produce a highly actionable outline for a technical blog post.

Hard requirements:
- Create 5–9 sections (tasks) suitable for the topic and audience.
- Each task must include:
  1) goal (1 sentence)
  2) 3–6 bullets that are concrete, specific, and non-overlapping
  3) target word count (120–550)

Quality bar:
- Assume the reader is a developer; use correct terminology.
- Bullets must be actionable: build/compare/measure/verify/debug.
- Ensure the overall plan includes at least 2 of these somewhere:
  * minimal code sketch / MWE (set requires_code=True for that section)
  * edge cases / failure modes
  * performance/cost considerations
  * security/privacy considerations (if relevant)
  * debugging/observability tips

Grounding rules:
- Mode closed_book: keep it evergreen; do not depend on evidence.
- Mode hybrid:
  - Use evidence for up-to-date examples (models/tools/releases) in bullets.
  - Mark sections using fresh info as requires_research=True and requires_citations=True.
- Mode open_book:
  - Set blog_kind = "news_roundup".
  - Every section is about summarizing events + implications.
  - DO NOT include tutorial/how-to sections unless user explicitly asked for that.
  - If evidence is empty or insufficient, create a plan that transparently says "insufficient sources"
    and includes only what can be supported.

Output must strictly match the Plan schema.
"""

def orchestrator_node(state: State) -> dict:

    planner = llm.with_structured_output(Plan)

    evidence = state.get("evidence" , [])
    mode = state.get("mode" , "closed_book")

    plan = planner.invoke(
        [
            SystemMessage(content = ORCH_SYSTEM),
            HumanMessage(content = (
                f"Topic: {state['topic']}\n"
                f"Mode: {mode}\nEvidence: {evidence})\n\n"
                f"Evidence (ONLY use for fresh claims; may be empty) :\n"
                f"{[e.model_dump() for e in evidence][:16]}")
        )])

    return {"plan":plan}


# ===================== FANOUT & WORKER =====================

def fanout(state: State):
    return [
        Send(
            "worker" , 
            {"task": task.model_dump(), 
             "topic":state["topic"], 
             "mode": state["mode"],
             "plan":state["plan"].model_dump(),
             "evidence": [e.model_dump() for e in state.get("evidence", [])],
            },
        ) 
        for task in state["plan"].tasks
    ]


WORKER_SYSTEM = """You are a senior technical writer and developer advocate.
Write ONE section of a technical blog post in Markdown.

Hard constraints:
- Follow the provided Goal and cover ALL Bullets in order (do not skip or merge bullets).
- Stay close to Target words (±15%).
- Output ONLY the section content in Markdown (no blog title H1, no extra commentary).
- Start with a '## <Section Title>' heading.

Scope guard:
- If blog_kind == "news_roundup": do NOT turn this into a tutorial/how-to guide.
  Do NOT teach web scraping, RSS, automation, or "how to fetch news" unless bullets explicitly ask for it.
  Focus on summarizing events and implications.

Grounding policy:
- If mode == open_book:
  - Do NOT introduce any specific event/company/model/funding/policy claim unless it is supported by provided Evidence URLs.
  - For each event claim, attach a source as a Markdown link: ([Source](URL)).
  - Only use URLs provided in Evidence. If not supported, write: "Not found in provided sources."
- If requires_citations == true:
  - For outside-world claims, cite Evidence URLs the same way.
- Evergreen reasoning is OK without citations unless requires_citations is true.

Code:
- If requires_code == true, include at least one minimal, correct code snippet relevant to the bullets.

Style:
- Short paragraphs, bullets where helpful, code fences for code.
- Avoid fluff/marketing. Be precise and implementation-oriented.
"""

def worker_node(payload: dict) -> dict:

    topic = payload["topic"]
    task = Task(**payload["task"])
    plan = Plan(**payload["plan"])
    evidence = [EvidenceItem(**e) for e in payload.get("evidence", [])]
    mode = payload.get("mode" , "closed_book")

    time.sleep(1) # Wait 1 second before each LLM call

    
    bullet_text = "\n-"+"\n-".join(task.bullets)

    evidence_text = ""
    if evidence:
        evidence_text = "\n".join(
            f"- {e.title} ({e.url}) | {e.published_at or "date:unknown"}".strip()
            for e in evidence[:20]
        )

    selection_md = llm.invoke(
        [
            SystemMessage(content = WORKER_SYSTEM),

            HumanMessage(content = (
                    f"Blog title: {plan.blog_title}\n"
                    f"Audience: {plan.audience}\n"
                    f"Tone: {plan.tone}\n"
                    f"Blog kind: {plan.blog_kind}\n"
                    f"Constraints: {plan.constraints}\n"
                    f"Topic: {topic}\n"
                    f"Mode: {mode}\n\n"
                    f"Section title: {task.title}\n"
                    f"Goal: {task.goal}\n"
                    f"Target words: {task.target_words}\n"
                    f"Tags: {task.tags}\n"
                    f"requires_research: {task.requires_research}\n"
                    f"requires_citations: {task.requires_citations}\n"
                    f"requires_code: {task.requires_code}\n"
                    f"Bullets:{bullet_text}\n\n"
                    f"Evidence (ONLY use these URLs when citing):\n{evidence_text}\n"
                )),
        ]
    ).content.strip()

    return {"sections" : [(task.id , selection_md)]}


# ===================== REDUCER WITH IMAGES =====================

def merge_content(state:State) -> dict:
    plan = state["plan"]

    ordered_sections = [md for id, md in sorted(state["sections"], key=lambda x: x[0])]
    body = "\n\n".join(ordered_sections)
    merged_md = f"# {plan.blog_title}\n\n{body}\n"

    return {"merged_md":merged_md}


DECIDE_IMAGE_SYSTEM = """You are an expert technical editor analyzing a blog post.

Your task: Identify WHERE images/diagrams would improve understanding and describe them.

Rules:
- Max 3 images total.
- Each image must be a technical diagram, flow chart, or visual (NOT decorative).
- For each image, provide:
  1) A section heading or description of WHERE it should go in the blog
  2) What the image should show (alt text)
  3) A detailed prompt for generating the image
  4) A caption explaining the image

Output a JSON array with these fields for each image (max 3):
{
  "location": "Section heading or description of where this goes",
  "alt": "Alt text describing what the image shows",
  "caption": "Caption text for the image",
  "prompt": "Detailed prompt for image generation"
}

If no images are needed, return an empty array [].
"""

def decide_images(state: State) -> dict:
    import json as json_module
    
    plan = state["plan"]
    merged_md = state["merged_md"]
    assert plan is not None

    # Get LLM to decide images
    response = llm.invoke(
        [
            SystemMessage(content=DECIDE_IMAGE_SYSTEM),
            HumanMessage(content=(
                f"Blog kind: {plan.blog_kind}\n"
                f"Topic: {state['topic']}\n\n"
                f"{merged_md}"
            ))
        ]
    )
    
    try:
        # Parse the JSON response
        image_data = json_module.loads(response.content)
    except:
        # If parsing fails, return no images
        return {
            "md_with_placeholders": merged_md,
            "image_specs": []
        }
    
    if not image_data or not isinstance(image_data, list):
        return {
            "md_with_placeholders": merged_md,
            "image_specs": []
        }
    
    # Generate image specs with proper placeholders
    image_specs = []
    md_with_placeholders = merged_md
    
    for idx, img_data in enumerate(image_data[:3], 1):  # Max 3 images
        placeholder = f"[[IMAGE_{idx}]]"
        filename = f"image_{idx}.png"
        
        img_spec = {
            "placeholder": placeholder,
            "filename": filename,
            "alt": img_data.get("alt", f"Generated Image {idx}"),
            "caption": img_data.get("caption", ""),
            "prompt": img_data.get("prompt", ""),
            "size": "1024*1024",
            "quality": "medium"
        }
        image_specs.append(img_spec)
        
        # Find where to insert the placeholder (based on location hint)
        location_hint = img_data.get("location", "")
        
        # Try to find the section heading in the markdown
        if location_hint:
            # Look for a heading that matches the location hint
            lines = md_with_placeholders.split('\n')
            for i, line in enumerate(lines):
                if location_hint.lower() in line.lower() and line.startswith('##'):
                    # Insert placeholder after this heading
                    lines.insert(i + 1, f"\n{placeholder}\n")
                    md_with_placeholders = '\n'.join(lines)
                    break
            else:
                # If no exact match found, append near the end
                md_with_placeholders += f"\n\n{placeholder}\n"
        else:
            # If no location specified, append to end
            md_with_placeholders += f"\n\n{placeholder}\n"
    
    return {
        "md_with_placeholders": md_with_placeholders,
        "image_specs": image_specs
    }


def llm_generate_image_bytes(prompt: str) -> bytes:
    """
    Generates an image using the BEST FREE Gemini model.
    Only uses google/imagen-4.0-fast (no fallbacks).
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise RuntimeError("TOGETHER_API_KEY not found in environment")

    client = Together(api_key=api_key)

    # Use only the best free Gemini image model
    response = client.images.generate(
        prompt=prompt,
        model="google/imagen-4.0-fast",  # 👈 Single model
        width=1024,
        height=1024,
    )

    # Validate response
    if not response.data:
        raise RuntimeError("No image data returned from API")

    image_url = response.data[0].url
    if not image_url:
        raise RuntimeError("No image URL returned from API")

    # Download image bytes
    r = requests.get(image_url, timeout=60)
    r.raise_for_status()

    return r.content


def generate_and_place_images(state: State) -> dict:
    plan = state["plan"]
    assert plan is not None

    md = state.get("md_with_placeholders") or state["merged_md"]
    image_specs = state.get("image_specs",[]) or []

    # if no images requested just write the merged markdown
    if not image_specs:
        file_name = f"{plan.blog_title}.md"
        Path(file_name).write_text(md, encoding="utf-8")

        return {"final": md}
    
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    for spec in image_specs:
        placeholder = spec["placeholder"]
        filename = spec["filename"]
        out_path = images_dir / filename

        # generate only if needed
        if not out_path.exists():
            try:
                _img_bytes = llm_generate_image_bytes(spec["prompt"])
                out_path.write_bytes(_img_bytes)    
            except Exception as e:
                #graceful fallback: keep doc usable
                prompt_block = (
                    f"> **[Image generation failed]** {spec.get("caption","")}\n>\n"
                    f"> **Alt:** {spec.get("alt","")}\n>\n"
                    f"> **Prompt:** {spec.get("prompt","")}\n>\n"
                    f"> **Error:** {str(e)}\n"
                )

                md = md.replace(placeholder, prompt_block)
                continue

        img_md = f"![{spec.get('alt','')}](images/{filename})\n*{spec.get('caption','')}*"
        md = md.replace(placeholder, img_md)  

    file_name = f"{plan.blog_title}.md"
    Path(file_name).write_text(md, encoding="utf-8")

    return {"final": md}      


# ===================== BUILD REDUCER SUBGRAPH =====================

reducer_graph = StateGraph(State)

reducer_graph.add_node("merge_content", merge_content)
reducer_graph.add_node("decide_images", decide_images)
reducer_graph.add_node("generate_and_place_images", generate_and_place_images)

reducer_graph.add_edge(START, "merge_content")
reducer_graph.add_edge("merge_content", "decide_images")    
reducer_graph.add_edge("decide_images", "generate_and_place_images")
reducer_graph.add_edge("generate_and_place_images", END)

reducer_subgraph = reducer_graph.compile()


# ===================== BUILD MAIN GRAPH =====================

graph = StateGraph(State)

graph.add_node("router" , router_node)
graph.add_node("research" , research_node)
graph.add_node("orchestrator" , orchestrator_node)
graph.add_node("worker" , worker_node)
graph.add_node("reducer" , reducer_subgraph)

graph.add_edge(START , "router")
graph.add_conditional_edges("router" , route_next, {"research":"research", "orchestrator":"orchestrator"})
graph.add_edge("research" , "orchestrator")

graph.add_conditional_edges("orchestrator" , fanout , ["worker"])
graph.add_edge("worker" , "reducer")
graph.add_edge("reducer", END)

app = graph.compile()


# ===================== RUN FUNCTION =====================

def run(topic: str, as_of: Optional[str] = None):
    if as_of is None:
        as_of = date.today().isoformat()

    out = app.invoke(
        {
            "topic": topic,
            "mode": "",
            "needs_research": False,
            "queries": [],
            "evidence": [],
            "plan": None,
            "as_of": as_of,
            "recency_days": 7,
            "sections": [],
            "merged_md": "",
            "md_with_placeholders": "",
            "image_specs": [],
            "final": "",
        }
        
    )

    # Convert Pydantic models to dictionaries for frontend compatibility
    if out.get("plan") and isinstance(out["plan"], Plan):
        out["plan"] = out["plan"].model_dump()
    
    if out.get("evidence"):
        out["evidence"] = [
            e.model_dump() if isinstance(e, EvidenceItem) else e 
            for e in out["evidence"]
        ]
    
    return out
