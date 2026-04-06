# Skill: Paper Ingestion — PDF Academic Paper Parsing via MinerU

This skill parses PDF academic papers into structured, machine-readable elements (equations, tables, algorithms, text blocks) using the MinerU API. The output feeds into planner's Paper Ingestion Mode, enabling the Paper-to-Package pipeline.

---

## Trigger Phrases

Any of the following user intents activate this skill. **Exact wording is NOT required** — leader routes semantically:

- "Read this paper and build a package"
- "Ingest this paper"
- "Parse this PDF"
- "Extract the estimator from this paper"
- "Turn this paper into an R/Python/Julia package"
- "Paper to package"
- Upload a PDF with any package-building intent

A short prompt like `"build a package from this paper"` with an attached PDF is sufficient.

---

## What This Skill Does

1. **Validate** — Check MinerU API token availability and PDF file accessibility
2. **Parse** — Upload PDF to MinerU API, retrieve structured output (Markdown + JSON)
3. **Extract** — Classify MinerU output into typed elements: equations, tables, text blocks, figures, algorithms
4. **Enrich** — Add contextual information (surrounding paragraphs, section hints, page numbers)
5. **Output** — Write `paper-elements.json` to the run directory for planner consumption

---

## Prerequisites

### MinerU API Token

This skill requires a MinerU API token from <https://mineru.net>.

**Detection sequence** (follows the same priority pattern as `skills/credential-setup/SKILL.md`):

1. **Environment variable**: `MINERU_API_TOKEN`
2. **`.env` file**: key `MINERU_API_TOKEN` or `mineru_api` (doc2md compatible) — search current directory, then up to 5 parent directories
3. **Ask user**: Prompt via `AskUserQuestion` with instructions to obtain a token

**Free tier**: 2000 pages/day at high priority. Sufficient for most single-paper workflows.

**Token verification**: Before parsing, the script validates the token with a lightweight API call. If invalid or expired, report clearly and stop.

### File Requirements

| Constraint | Limit |
| --- | --- |
| Max file size | 200 MB |
| Max page count | 600 pages |
| Supported formats | PDF (native + scanned), DOCX, images (PNG, JPG) |

---

## Workflow Integration

### Workflow 14: Paper-to-Package

```
leader → paper-ingestion (this skill) → planner (paper mode) → [HOLD: confirm]
  → planner (generate specs) → builder → tester → scriber → reviewer → shipper?
```

**Key integration points**:

1. Leader detects PDF upload or paper-ingestion intent
2. Leader verifies MinerU API token (adds to `credentials.md`)
3. Leader runs `parse_paper.py` to parse the PDF
4. Leader runs `extract_elements.py` to classify elements
5. `paper-elements.json` is written to the run directory
6. Leader dispatches planner with `paper-elements.json` path — planner enters Paper Ingestion Mode
7. Planner MUST HOLD to confirm comprehension with the user before generating specs

### State Machine Extension

Paper ingestion adds one state to the standard model:

```
CREDENTIALS_VERIFIED → NEW → PLANNED → PAPER_PARSED → SPEC_READY → ...
```

**`PAPER_PARSED` preconditions**:
- `paper-elements.json` exists in the run directory
- JSON passes schema validation
- At least one equation OR one table was extracted (empty extraction = likely parse failure)

---

## MinerU API Protocol (v4 — Presigned URL Flow)

### Step 1 — Request Presigned Upload URL

```
POST https://mineru.net/api/v4/file-urls/batch
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "files": [{"name": "paper.pdf", "is_ocr": false}],
  "model_version": "vlm",
  "enable_formula": true,
  "enable_table": true,
  "language": "en"
}
```

Response: `{ "code": 0, "data": { "batch_id": "...", "file_urls": ["<presigned_url>"] } }`

### Step 2 — Upload File to Presigned URL

```
PUT <presigned_url>
Body: <raw PDF bytes, NO extra headers>
```

The presigned URL points to Alibaba Cloud OSS. Send raw bytes with no `Content-Type` header — OSS includes Content-Type in the signature, so any extra or mismatched header causes `SignatureDoesNotMatch` errors.

### Step 3 — Poll for Completion

```
GET https://mineru.net/api/v4/extract-results/batch/{batch_id}
Authorization: Bearer <token>
```

Poll every 5 seconds. Timeout after 10 minutes.

Response states (in `data.extract_result[0].state`): `pending`, `running`, `done`, `failed`

On `done`: response includes `full_zip_url` for downloading results.

### Step 4 — Download Results

```
GET <full_zip_url>
```

CDN URL — no authorization header needed.

Returns a ZIP containing:
- `content_list_v2.json` — page-grouped elements (v2 format: list of pages, each page a list of elements)
- `content_list.json` — flat element list (v1 fallback)
- `*.md` — full Markdown rendering
- `images/` — extracted figures and equation images

---

## Output Format: `paper-elements.json`

The extraction script transforms MinerU's `content_list_v2.json` (page-grouped format; falls back to `content_list.json` v1) into a StatsClaw-native format:

```json
{
  "metadata": {
    "title": "Synthetic Control Methods for Comparative Case Studies",
    "source_file": "abadie2010.pdf",
    "total_pages": 42,
    "parse_model": "vlm",
    "parsed_at": "2026-04-06T10:30:00Z",
    "mineru_version": "3.0"
  },
  "equations": [
    {
      "id": "eq_001",
      "type": "interline_equation",
      "latex": "\\hat{\\alpha}_1 = Y_{1t} - \\sum_{j=2}^{J+1} w_j^* Y_{jt}",
      "page": 5,
      "context_before": "The synthetic control estimator is defined as...",
      "context_after": "where $w_j^*$ are the optimal weights..."
    }
  ],
  "tables": [
    {
      "id": "tbl_001",
      "caption": "Table 1: Monte Carlo Simulation Results",
      "html": "<table>...</table>",
      "page": 12,
      "has_formulas": true,
      "context_before": "Table 1 reports the bias and RMSE..."
    }
  ],
  "algorithms": [
    {
      "id": "alg_001",
      "title": "Algorithm 1: Synthetic Control Method",
      "raw_text": "Step 1: Select donor pool...\nStep 2: Solve optimization...",
      "page": 7,
      "has_inputs_outputs": true,
      "referenced_equations": ["eq_001", "eq_003"]
    }
  ],
  "text_blocks": [
    {
      "id": "txt_001",
      "content": "We consider the problem of estimating...",
      "page": 1,
      "section_hint": "Introduction"
    }
  ],
  "figures": [
    {
      "id": "fig_001",
      "caption": "Figure 1: Estimated treatment effect",
      "image_path": "images/fig_001.jpg",
      "page": 8
    }
  ],
  "summary": {
    "total_equations": 25,
    "total_inline_equations": 48,
    "total_tables": 4,
    "total_algorithms": 1,
    "total_figures": 6,
    "total_text_blocks": 87
  }
}
```

---

## Algorithm Block Detection

MinerU does not natively identify algorithm/pseudocode blocks as a distinct type. The extraction script applies heuristic detection to promote text blocks to `algorithms`:

### Detection Rules

A text block is reclassified as an algorithm if ANY of:

1. **Keyword header**: starts with "Algorithm [N]" (case-insensitive, with optional colon or period)
2. **I/O declarations**: contains "Input:", "Output:", "Return:", or "Require:" within the first 3 lines
3. **Pseudocode density**: contains >= 5 pseudocode keywords (`for`, `while`, `if`, `then`, `else`, `repeat`, `until`, `do`, `end`, `return`) AND text is < 200 words (filters out long prose paragraphs that merely discuss algorithms)
4. **Numbered steps with control flow**: has >= 3 numbered lines (e.g., "1.", "2.") AND contains at least one control flow keyword AND text is < 200 words

### Equation Cross-Referencing

For each detected algorithm, the script scans for equation references:
- Pattern: `(N)`, `Eq. N`, `equation N`, `Eq. (N)` where N is a number
- Matched references are linked to entries in `equations[]` by page proximity

### Quality Notes

- **Expected true positive rate**: >= 80% for standard algorithm environments
- **Expected false positive rate**: <= 10%
- Algorithm detection is best-effort; planner's semantic understanding compensates for missed blocks

---

## Error Handling

| Error | Script Behavior | Leader Action |
| --- | --- | --- |
| Token missing | Exit with code 1 + message | Ask user for token via `AskUserQuestion` |
| Token invalid/expired | Exit with code 2 + message | Ask user to regenerate at mineru.net |
| File too large (> 200MB) | Exit with code 3 + message | Report to user, suggest splitting |
| File too many pages (> 600) | Exit with code 4 + message | Report to user, suggest page range |
| API timeout (> 10 min) | Exit with code 5 + message | Retry once; if still fails, HOLD |
| Parse failure (API error) | Exit with code 6 + API error | Report to user, suggest alternative format |
| Empty extraction (0 equations + 0 tables) | Exit with code 7 + warning | Warn user: "No mathematical content detected — is this the right paper?" |
| Daily quota exceeded | Exit with code 8 + message | Suggest waiting or using local MinerU |
| Network error | Exit with code 9 + message | Check connectivity, retry once |

---

## Script Reference

### `scripts/parse_paper.py`

```
Usage: python parse_paper.py --input <path> --output <dir> [--model vlm|pipeline] [--check-token]

Options:
  --input       PDF file path (required)
  --output      Output directory for MinerU results (required)
  --model       Parse model: "vlm" (default, highest accuracy) or "pipeline" (faster)
  --check-token Validate token and exit (for credential verification)
  --timeout     API timeout in seconds (default: 600)
```

### `scripts/extract_elements.py`

```
Usage: python extract_elements.py --input <content_list_v2.json> --output <paper-elements.json> [--markdown <file.md>]

Options:
  --input       MinerU content_list_v2.json (or v1) path, or directory containing it (required)
  --output      Output paper-elements.json path (required)
  --markdown    MinerU markdown file for additional context extraction (optional)
  --images-dir  Directory containing extracted images (optional, default: images/)
```

---

## Caching

Parsed results are cached in `.repos/workspace/<repo-name>/tmp/paper-cache/` keyed by SHA-256 of the input file. If the same PDF is re-parsed, cached results are returned immediately without an API call. Cache entries older than 30 days are eligible for cleanup.

---

## Limitations

1. **No bibliographic metadata**: MinerU does not extract structured author lists, abstracts, or reference lists. For citation parsing, consider GROBID as a complementary tool (future enhancement).
2. **Algorithm detection is heuristic**: Pseudocode blocks without standard formatting may be missed. Planner compensates with semantic analysis.
3. **Scanned PDF quality varies**: OCR accuracy depends on scan quality. Very old or low-resolution scans may produce unusable output.
4. **MinerU API dependency**: Requires internet access and a valid token. For air-gapped environments, local MinerU deployment is needed (not covered by this skill).
