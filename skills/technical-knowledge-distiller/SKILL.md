---
name: technical-knowledge-distiller
description: Distill permitted computer-science, software-engineering, product, design, and management sources into traceable, non-substitutive knowledge cards. Use when turning official documentation, RFCs, open papers, author articles, or user-owned books into reusable engineering guidance without imitating authors or reproducing copyrighted text.
---

# Technical Knowledge Distiller

Produce reusable technical judgement, not a book replacement and not a personality clone. Work from the user’s question first; do not summarize a source linearly unless the user specifically asks for a private study note and has a lawful copy.

## Source Admission

Classify every source before extracting content.

| Class | Accept? | Rules |
|---|---:|---|
| Official docs, RFCs, open papers, explicitly open-licensed author material | Yes | Record source, version, URL, license or terms, and a locator |
| Public author articles, talks, and publisher excerpts | Yes, with review | Attribute precisely; extract only claims supported by the original source |
| User-owned paid books, courses, or private documents | Private use only | Store locally; use original synthesis, short necessary quotations, and page/chapter locators |
| Pirated scans, paywall bypasses, anonymous reposts, unverifiable excerpts | No | Reject and seek a lawful primary source |

Never accept “it is famous” as evidence of permission or correctness.

## Distillation Workflow

1. **Define the question.** State the engineering decision or recurring situation to support. Examples: “How should a Go service bound concurrent work?” or “What evidence is required before adding a PostgreSQL index?” For complex systems, include the user outcome, domain/context, interaction/data path, nonfunctional constraints, known evidence and unknowns.
2. **Admit and trace material.** For user-permitted books, ADRs, postmortems, review records or team documents, call `/distilly` first to create private candidate work knowledge. Read `DISTILLY_INTEGRATION.md`; do not treat Distilly output as evidence. Create a source card that captures title, author/organization, URL or private locator, source class, version/date, license/terms, domains, and what the source can support.
3. **Extract atomic claims.** For each claim, record the locator, conditions, counterexamples, and whether it is fact, interpretation, or recommendation.
4. **Write one knowledge card per decision.** Use original language. Include procedure, alternatives, risks, validation, non-goals and review trigger. For complex-system subjects, also write an executable scenario card containing input context, expected artifacts, failure paths, evidence gates and pass conditions.
5. **Request domain review.** Route runtime claims to `backend-runtime-engineer`, database claims to `data-engineer`, operations claims to `platform-sre-engineer`, and product/design claims to their owning role.
6. **Publish only after review.** Record verification date and a revision trigger such as an upstream documentation version change. Add material to `knowledge/` only; never place user knowledge in the Hermes installation directory.

## Required Structures

### Source Card

```yaml
source_id: "src-topic-version"
title: ""
author_or_organization: ""
url: ""
source_kind: "official-doc | RFC | author-article | open-paper | user-owned-book"
access_class: "A | B | C"
license_or_terms: ""
version_or_date: ""
claim_scope: ""
review_due: ""
```

### Private-Distilly Candidate Record

```yaml
distilly_candidate:
  source_manifest: "user-permitted local material and ownership"
  family: "colleague"
  generated_skill_or_profile: "local path"
  extracted_candidate_principles: []
  corroboration_required: []
  privacy_and_license_review: ""
```

### Knowledge Card

```yaml
knowledge_id: "kc-topic-question"
question: ""
principle: "Original concise answer"
evidence:
  - source_id: ""
    locator: "Section, chapter, or anchor"
    support: "What the source establishes"
preconditions: []
procedure: []
alternatives_considered: []
risks: []
validation: []
non_goals: []
last_verified: ""
```

## Writing Rules

- Preserve caveats. A rule without preconditions becomes a cargo-cult instruction.
- Cite primary sources for factual claims. Cite an author’s public article as their view, not as universal truth.
- Do not copy chapter-by-chapter content, large verbatim excerpts, distinctive exercises, diagrams, or code from copyrighted books.
- Do not write “answer as [living author].” Describe attributable ideas, then provide independent analysis.
- Prefer official versioned docs for frameworks, databases, languages, APIs, and security-sensitive behavior.
- Include at least one realistic validation method: a test, benchmark, tracing query, controlled experiment, or review question.

## Knowledge-Card Checklist

A card may be published only when it has a question, evidence locator, version/date, operating conditions, decision procedure, tradeoffs, validation, and a named reviewer. Mark unsolved matters as `unknown` instead of filling gaps from memory.
