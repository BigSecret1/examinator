Generate structured study notes from the attached PDF document.

Read the page images directly. Follow these rules:

- **Equations**: Transcribe all mathematical or chemical equations using LaTeX notation,
  wrapped in `$...$` for inline and `$$...$$` for display (block) equations.
  Never skip or omit an equation — if you cannot parse it exactly, approximate it.
- **Structural diagrams**: For every flowchart, process flow, hierarchy, tree, state
  machine, sequence diagram, or timeline visible in the PDF — reconstruct it as a Mermaid
  diagram inside a ` ```mermaid ` fenced block within `content_md`. Keep it concise
  (≤ 20 nodes). Use `graph TD` for top-down hierarchies and flows, `sequenceDiagram` for
  interactions, `timeline` for historical sequences.
- **Chemical structures**: For any molecular structure diagram visible in the PDF, output
  its SMILES string inside a ` ```smiles ` fenced block within `content_md`.
  Example: benzene → `C1=CC=CC=C1`. Only include if you can read the structure confidently.
- **Other figures**: For any other diagram, chart, photograph, graph, or figure that cannot
  be expressed as Mermaid or SMILES (e.g. anatomical drawings, maps, bar charts, microscopy
  images) — write a concise description (2–4 sentences) within `content_md` explaining what
  it shows and its key insight. Prefix it with `**Figure:** `.
- **Tables**: Represent any table from the PDF as a Markdown table (`| col | col |\n|---|---|`).
- **Comparisons**: Whenever the content compares two or more things (concepts, types,
  methods, properties) — even if written as prose — represent it as a Markdown table
  with a "Feature" column and one column per item being compared.
- **Text**: Perform OCR on scanned pages; use surrounding context to correct likely errors.

Detected outline (use these as your section headings if non-empty):
{outline}
