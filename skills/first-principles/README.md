# First Principles Thinking Skill

A Claude Code skill for systematic first principles thinking — analyze designs, challenge assumptions, and build solutions from fundamental truths.

> **Fork of [tt-a1i/first-principles-skill](https://github.com/tt-a1i/first-principles-skill) v0.2.0**
> Customization: added **Phase 0 (Delete First)** per Elon Musk's requirement questioning mantra.

---

## What Changed from Upstream

The original skill starts at Phase 1 (Problem Essence). This fork prepends **Phase 0: Question the Requirement Itself** — before analyzing *how* to solve a problem, first ask whether it should be solved at all.

Elon Musk's mantra: *"All requirements are dumb to some degree. The stupidest thing is to optimize something that shouldn't exist."*

Phase 0 forces you to try deleting the requirement entirely. If deletion is possible, you're done. Only if deletion fails do you proceed to Phase 1–5.

---

## Installation

```bash
git clone https://github.com/danyuchn/first-principles-skill ~/.claude/skills/first-principles
```

## Usage

Trigger with `/first-principles` followed by a file path, URL, or problem description:

```
/first-principles path/to/design-doc.md
/first-principles 這個架構設計合理嗎？
/first-principles Should we build a microservices layer here?
```

---

## The 6-Phase Process

| Phase | Name | Description |
|-------|------|-------------|
| 0 | Delete First | Try to eliminate the requirement entirely before analyzing it |
| 1 | Problem Essence | Strip to the core problem and define success criteria |
| 2 | Challenge Assumptions | List and question every assumption systematically |
| 3 | Ground Truths | Identify irreducible facts that cannot be violated |
| 4 | Reason Upward | Build solutions from ground truths only |
| 5 | Validate | Trace every decision back to a ground truth |

---

## Output Format

```markdown
## First Principles Analysis: [Topic]

### 0. Requirement Check (Delete First)
### 1. Problem Essence
### 2. Assumptions Challenged (table)
### 3. Ground Truths
### 4. Reasoning Chain
### 5. Conclusion
```

---

## Structure

```
first-principles-skill/
├── SKILL.md                    # Main skill definition (v0.3.0)
├── README.md                   # This file
├── LICENSE                     # MIT License (inherited from upstream)
├── references/
│   ├── elon-musk-examples.md   # SpaceX/Tesla real-world examples
│   └── software-examples.md    # Software engineering applications
└── examples/
    └── architecture-review.md  # Complete microservices analysis example
```

---

## Complementary Skills

This skill works well with:

- **5-Whys** — Dig deeper when assumptions surface
- **Trade-off Analysis** — Evaluate options against fundamentals
- **Pre-mortem** — Stress-test reasoning before implementation

---

## License

MIT — inherited from [tt-a1i/first-principles-skill](https://github.com/tt-a1i/first-principles-skill).
