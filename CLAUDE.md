# Hundred Schools Debate

CrewAI-based multi-agent debate app. Each agent role-plays a Chinese philosophical school (Confucianism, Daoism, Legalism, etc.) and debates modern questions. **Every argument must cite actual classical text passages — no generated or paraphrased citations.**

## Tech Stack
- Python 3.12+
- CrewAI (multi-agent orchestration)
- LangChain/OpenAI-compatible LLM client (for manager_llm if needed)
- Local vector store or keyword index for classical text retrieval

## Project Structure
```
hundred-schools-debate/
├── CLAUDE.md
├── pyproject.toml
├── .env.example
├── src/
│   ├── debate/
│   │   ├── agents/          # One module per school (confucian.py, daoist.py, legalist.py)
│   │   ├── tasks/           # Task definitions per debate round
│   │   ├── tools/           # Classical text retrieval tool
│   │   └── crew.py          # Crew assembly
│   └── corpus/              # Classical texts (Lunyu, Daodejing, Han Feizi, etc.)
│       └── index/           # Pre-built retrieval index
└── tests/
```

## Architecture Rules

### Process: Sequential ONLY
Use `Process.sequential`. **Never use `Process.hierarchical`** unless explicitly instructed. Hierarchical mode introduces a manager LLM that can re-delegate tasks indefinitely, causing the exact Repeat Thoughts spiral this project must avoid.

### Delegation: OFF for debaters
All debater agents must have `allow_delegation=False`. The judge agent also `allow_delegation=False`. Debate is a directed acyclic flow: each debater speaks once per round, then the judge evaluates. No agent may delegate to another.

### Citation: Retrieval-Augmented, never generative
The LLM must **not** generate classical quotations from memory. Two approved patterns:

**Pattern A (small corpus):** Inject candidate passages into the Task `description`. Instruct: "Select at most 2 passages from the provided excerpts. If none are relevant, say so explicitly."

**Pattern B (scale):** Give each debater agent a `ClassicalTextRetrievalTool`. The Task description instructs: "Use the retrieval tool to find relevant passages before forming your argument. Cite only passages returned by the tool."

Reject any implementation where the LLM produces a quotation without a retrieval step or injected source list.

### Citation: retrieval and citation are separate concerns
The text used to *find* a passage need not be the text used to *cite* it.
- Retrieval index MAY use `modern_gloss` (or `theme_tags` / `concept_tags`) to improve matching against modern-Chinese debate questions.
- `cited_passages` MUST contain only `original_text` (文言文), with its `source`.
- Any tool returning retrieval results must label fields explicitly:
  `original_text` (citable) vs `modern_gloss` (context only, NOT citable).

**Pattern B (scale), concrete requirements:** The `ClassicalTextRetrievalTool` MUST:
1. Filter by `school` (agent's own school only) and, when possible, by
   `theme_tags` / `concept_tags` derived from the debate question.
2. Match using `modern_gloss` and/or tags — NOT raw `original_text` alone,
   because classical Chinese vocabulary rarely matches modern-Chinese queries.
3. Return entries with fields explicitly separated:
   `original_text` + `source` (citable), and `modern_gloss` (context only).

Task description for Pattern B: "Cite only passages returned by the tool. Quote only from the `original_text` field; never cite `modern_gloss`."

### Two indexes, not one
Build and maintain two separate artifacts from the same JSONL corpus:
- **Retrieval index** — built from `modern_gloss` + `theme_tags` + `concept_tags`. Used to *find* candidate passages for a modern-Chinese question.
- **Citation corpus** — built from `original_text` + `source` only. Used to *verify* that every quoted passage actually exists in the corpus.

Never merge these into a single index. The retrieval index optimizes for recall; the citation corpus optimizes for verifiability.

## Corpus Schema (JSONL)

Each classical text is processed into JSONL entries with these fields:

```json
{
  "id": "lunyu-xueer-01",
  "source": "《论语·学而》",
  "school": "儒家",
  "original_text": "子曰：学而时习之，不亦说乎？...",
  "modern_gloss": "孔子说：学了又按时温习实践...",
  "theme_tags": ["学习", "实践", "君子", "修养"],
  "concept_tags": ["学", "习", "君子", "愠"],
  "debate_angles": ["可用于论证'学习与实践结合'的价值", "..."],
  "notes": "适合作为儒家'修身'立场的开篇引证。"
}
```

Field roles:
- `original_text` + `source`: the only fields allowed in `cited_passages`.
- `modern_gloss`: retrieval aid and Agent comprehension aid; never citable.
- `theme_tags` / `concept_tags`: filtering and keyword matching.
- `debate_angles`: hint to the Agent on how the passage may be used.
- `notes`: human-facing maintenance notes only.

## Agent Conventions
- `role`: School name + "Debater" (e.g., "Confucian Debater")
- `goal`: "Argue from the [School] perspective on the given question, citing classical sources"
- `backstory`: 2-3 sentences on core concepts (e.g., ren, li, wuwei, fa/shu/shi). Keep it short — verbose backstories dilute routing signals and waste tokens.
- `allow_delegation=False` — always.

## Task Conventions
- `expected_output`: Must be machine-checkable where possible. For arguments: a structured format with `claim`, `reasoning`, `cited_passages` (list of exact quotes from `original_text` + `source`). For judge: `winner` (school name or "draw") + `rationale`.
- Do **not** write subjective criteria like "compelling argument" or "high quality". The judge LLM will loop trying to satisfy vague standards.

## Workflow (for feature work)
1. Read existing agent/task modules before adding a new school.
2. For new school: create `agents/<school>.py`, add to `crew.py`, process the school's classical text into JSONL, then rebuild both indexes (retrieval + citation).
3. For citation changes: update the retrieval tool, the Task description prompt, and the citation verification test **together**. Never change one without the others.
4. Run `pytest tests/test_citation.py` after any citation-related change. This test verifies every cited passage exists in the citation corpus.

## Commands
```bash
# Run a debate
python -m src.debate.crew --question "Should AI have legal rights?"

# Process a classical text into JSONL
python scripts/process_classics.py --book lunyu --input lunyu.txt --output corpus/lunyu.jsonl

# Build retrieval index (from modern_gloss + tags, for matching modern questions)
python scripts/build_index.py --mode retrieval

# Build citation corpus (original_text + source only, used for verification)
python scripts/build_index.py --mode citation

# Run citation integrity tests
pytest tests/test_citation.py -v
```

## What NOT to do
- Do not add `allow_delegation=True` to any agent without explicit instruction.
- Do not change `Process.sequential` to hierarchical.
- Do not let an agent produce a `cited_passages` field without a preceding retrieval call or injected source list in the same task context.
- Do not write `expected_output` with words like "good", "compelling", "high-quality", "convincing".
- Do not index `original_text` alone for retrieval. Always build the retrieval index from `modern_gloss` / tags.
- Do not allow `modern_gloss` content to appear inside `cited_passages`.
- Do not merge the retrieval index and the citation corpus into a single artifact.

## Known Pitfalls (from prior experience)
- **Repeat Thoughts spiral**: Caused by vague `expected_output` + delegation loops. Always make output criteria enumerable.
- **Citation hallucination**: LLMs invent plausible-sounding classical quotes. The retrieval tool is non-negotiable for citation fields, and `cited_passages` must be verified against the citation corpus.
- **Manager re-delegation**: Hierarchical process managers re-assign tasks when unsatisfied. Sequential + delegation off prevents this structurally.
- **Classical-Chinese retrieval miss**: Indexing only `original_text` causes low recall against modern-Chinese questions (documented ~0.40 vs ~0.81 hit@10 when using translations for retrieval). Always build the retrieval index from `modern_gloss` / tags, while keeping citation output strictly `original_text`.