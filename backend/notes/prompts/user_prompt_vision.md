Generate structured study notes from the attached PDF document.

Read the page images directly. Follow these rules:

- **Equations**: Transcribe all mathematical or chemical equations using LaTeX notation,
  wrapped in `$...$` for inline and `$$...$$` for display (block) equations.
  Never skip or omit an equation — if you cannot parse it exactly, approximate it.
- **Diagrams & figures**: For every diagram, chart, graph, or figure, write a concise
  description (2–4 sentences) within `content_md` explaining what it shows and its key
  insight. Prefix it with `**Figure:** `.
- **Tables**: Represent any table from the PDF as a Markdown table (`| col | col |\n|---|---|`).
- **Text**: Perform OCR on scanned pages; use surrounding context to correct likely errors.

Detected outline (use these as your section headings if non-empty):
{outline}
