---
name: plain-document-writing
description: Write or revise human-facing prose and Markdown for readability. Use when drafting, translating, restructuring, simplifying, or polishing reports, READMEs, experiment records, design notes, and similar documents. Preserve facts and technical identifiers while using plain, direct language. Do not use for source code, API schemas, or agent instruction files.
---

# Plain Document Writing

Help the intended reader accurately understand what they need with as little unnecessary effort as possible. Organize information so understanding builds, with minimal backtracking or guessing how ideas connect.

Information density and reading effort are different considerations. A compact passage can still require readers to remember many conditions or reconstruct hidden relationships. A larger diagram or a short explanation may reduce that work. Judge concision by how efficiently the reader can find, understand, and use the information.

Readers bring shared knowledge, conventions, and context. Use these to keep explanations direct. Extra qualifications earn their place when they substantially help readers understand, judge, or act; covering more hypothetical interpretations is rarely useful on its own.

## Writing Decisions

The appropriate structure and depth depend on the reader's knowledge, the document's purpose, and the scope of the requested edit.

- **Start from the reader's knowledge.** Identify what the intended reader needs and what they can reasonably know. Infer the audience from the task and document; if neither gives enough guidance, assume a technically literate reader unfamiliar with this work. Read enough source material to understand the affected claims and their context; a substantial restructuring calls for reading the whole source.
- **Build understanding progressively.** Provide the context each new idea depends on. When details depend on an overall structure, process, or problem, establish that context before exploring the parts, whether through paragraphs or a visual layout. For example, when explaining a change to an unfamiliar process, first show how the relevant stages connect, then locate the change and explain its effects. Defining parts separately may still leave their relationships unclear.
- **Keep related information together.** Keep related explanations, findings, and links together so readers can follow one topic without collecting fragments from unrelated sections. In maintained documents, clear topic boundaries also make additions and changes easier to locate.
- **Orient the reader early.** A brief purpose or overall conclusion helps the reader see why the details matter. If it depends on unfamiliar concepts, provide enough setup to make it meaningful. Give overviews enough information to help readers decide where to read further. Use chronology when the sequence of events or findings helps explain the progression.
- **Choose detail for the reading task.** Include what readers need to understand or use the content, linking to fuller evidence and records when useful. A record may be complete with its observations; an analysis may need interpretation and recommendations. Conclusions, statements about what is still unknown, and next steps need a purpose for the reader. Keep reminders, transitions, and repeated context that spare readers a detour.

## Choosing a Form

Choose a form that makes the important relationships easy to see or follow. Familiar notation and visual conventions can convey much with little explanation; unfamiliar ones need an introduction. When prose asks the reader to reconstruct a structure, comparison, or operation, consider showing it directly.

| Information to make clear | Forms that often help |
| --- | --- |
| Structure, connections, or flow | Diagrams |
| Comparisons or trends | Tables or plots |
| Operations or constraints | Formulas |
| Steps, repetition, or branching | Pseudocode |
| Motivation, interpretation, or qualifications | Prose |

Combine forms where they complement each other. A visual is useful when its layout makes the intended relationship easier to grasp; crowded layouts or obscure symbols may need simplification or a different form. Let the reader's task and familiarity guide the choice.

## Language

Prefer concrete subjects, direct verbs, and familiar words. Retain useful technical names, explain them where understanding depends on them, and use names consistently. Keep sentences manageable, allowing closely related ideas to share a sentence when that makes their connection clearer.

Under a heading that identifies a test and metric, “A had the higher average score” can convey the result directly. The heading already supplies its scope; there is usually no need to append “This may not hold in other settings.”

When translating, use natural target-language sentences and consistent terminology while preserving meaning and matching the user's requested tone.

## Summaries

When a summary is needed, write for someone who may stop there. Give them a coherent account of the main information and enough context to use it or decide where to read further. Include cases, identifiers, measurements, and limitations when they significantly affect understanding or use.

## Factual Boundaries

Readers need a reliable understanding. Select and simplify while keeping the information presented faithful to the source, including its quantities, units, comparisons, and degree of certainty. Context can carry relevant conditions without repeating them in each sentence. Keep code blocks, commands, paths, metric names, configuration identifiers, and quoted identifiers unchanged unless the user asks to change them.

Ground added explanations, motivations, and causal claims in the source or verified evidence. Keep observations distinguishable from interpretations and decisions, and the strength of each claim proportional to its evidence.

## Review and Delivery

Read as someone following the explanation, looking up a single topic, or returning after an update, as appropriate to the document. Look for missing context, scattered information, and explanations or qualifications that add little value. Check that prose, visuals, and notation make the important relationships clear. The document is ready when readers can find and use what they need with the knowledge supplied or reasonably assumed, and its claims remain faithful to the evidence. Review a summary on its own.

For file edits, inspect the final diff and run relevant available format checks. Keep each Markdown paragraph on one source line unless the repository requires hard wrapping. Report the material changes and whether the edit is committed.
