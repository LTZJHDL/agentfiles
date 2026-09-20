---
name: plain-document-writing
description: Write or revise human-facing prose and Markdown for readability. Use when drafting, translating, restructuring, simplifying, or polishing reports, READMEs, experiment records, design notes, and similar documents. Preserve facts and technical identifiers while using plain, direct language. Do not use for source code, API schemas, or agent instruction files.
---

# Plain Document Writing

Help the intended reader accurately understand what they need with as little unnecessary effort as possible. Organize information so understanding builds, with minimal backtracking or guessing how ideas connect.

Information density and reading effort are different considerations. A compact passage can still require readers to remember many conditions or reconstruct hidden relationships. A larger diagram or a short explanation may reduce that work. Judge concision by how efficiently the reader can find, understand, and use the information.

## Writing Decisions

The appropriate structure and depth depend on the reader's knowledge, the document's purpose, and the scope of the requested edit.

- **Start from the reader's knowledge.** Identify what the intended reader needs and what they can reasonably know. Infer the audience from the task and document; if neither gives enough guidance, assume a technically literate reader unfamiliar with this work. Read enough source material to understand the affected claims and their context; a substantial restructuring calls for reading the whole source.
- **Build understanding progressively.** Provide the context each new idea depends on. When details depend on an overall structure, process, or problem, establish that context before exploring the parts, whether through paragraphs or a visual layout. For example, when explaining a change to an unfamiliar process, first show how the relevant stages connect, then locate the change and explain its effects. Defining parts separately may still leave their relationships unclear.
- **Orient the reader early.** A brief purpose or overall conclusion helps the reader see why the details matter. If it depends on unfamiliar concepts, provide enough setup to make it meaningful. Use chronology when the sequence of events or findings helps explain the progression.
- **Choose detail for the reading task.** Include the context and evidence needed to follow the explanation and use its conclusions. Link to fuller records for verification and deeper reading. Keep reminders, transitions, and repeated context that spare readers a detour; remove repetition that adds no understanding.

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

Make actions and outcomes explicit. If the source says files were transferred but their contents have not been checked, “The transfer is complete; the contents have not been checked” distinguishes completion from validation. “The transfer succeeded” leaves that distinction unclear.

When translating, use natural target-language sentences and consistent terminology while preserving meaning and matching the user's requested tone.

## Summaries

When a summary is needed, write for someone who may stop there. Bring the main points together into a coherent answer to the reader's main question, with enough context and evidence to interpret it and the limitations that most affect its use. Include individual cases, identifiers, or measurements when they materially affect the overall interpretation or support a decision.

## Factual Boundaries

Readers need a reliable understanding, so clarity must stay faithful to the evidence. Preserve factual quantities, units, conditions, comparisons, and uncertainty. Keep code blocks, commands, paths, metric names, configuration identifiers, and quoted identifiers unchanged unless the user asks to change them.

Base added explanations on the source or verified evidence. Distinguish observations, interpretations, and decisions, and keep the strength of each claim proportional to its evidence. A smoother narrative must not introduce unsupported motivations, causal links, or conclusions.

## Review and Delivery

Follow the intended reading path, including movement between prose, visuals, and notation. Look for missing context, unclear references, and relationships the reader must reconstruct. Check whether compact wording hides necessary explanations and whether visuals make the relevant relationships easier to understand. The document is ready when the reader can follow its main explanation and use its conclusions with the knowledge supplied or reasonably assumed, and the claims remain faithful to the evidence. Review a summary on its own.

For file edits, inspect the final diff and run relevant available format checks. Keep each Markdown paragraph on one source line unless the repository requires hard wrapping. Report the material changes and whether the edit is committed.
