Generate structured study notes from the document below.

Follow these rules:

- **Equations**: Transcribe all mathematical or chemical equations using LaTeX notation,
  wrapped in `$...$` for inline and `$$...$$` for display (block) equations.
- **Tables**: Represent any table as a Markdown table (`| col | col |\n|---|---|`).
- **Comparisons**: Whenever the content compares two or more things (concepts, types,
  methods, properties) — even if written as prose — represent it as a Markdown table
  with a "Feature" column and one column per item being compared.
- **Structural diagrams**: Whenever the text describes or references a flowchart, process
  flow, hierarchy, tree, state machine, sequence of steps, or timeline — reconstruct it
  as a Mermaid diagram inside a ` ```mermaid ` fenced block within `content_md`. Keep it
  concise (≤ 20 nodes). Use `graph TD` for top-down hierarchies and flows, `sequenceDiagram`
  for interactions, `timeline` for historical sequences.
- **Chemical structures**: For any molecule or chemical compound named in the text, output
  its SMILES string inside a ` ```smiles ` fenced block within `content_md`.
  Example: benzene → `C1=CC=CC=C1`. Only include if the compound has a well-known SMILES.
- **Emphasis**: Use `**bold**` for key terms and `*italic*` for definitions or emphasis.

Detected outline (use these as your section headings if non-empty):
{outline}

--- BEGIN DOCUMENT TEXT ---
{text}
--- END DOCUMENT TEXT ---
