---
name: playbook-builder
description: Turn a repeated job, process, or task the user does manually into a written playbook (a SKILL.md) that can be run without them. Use whenever the user says "turn this into a playbook", "make this a skill", "document this process", "write this up so I don't have to explain it again", "turn this into an SOP", asks to capture a repeated job, or describes doing the same task over and over. Runs a structured interview, writes a Purpose/When-to-use/Inputs/Steps/Decisions/Definition-of-done/Edge-cases playbook, files any reusable templates or scripts with placeholders and an index, and adds verifiable definition-of-done checks that get run and reported on every future use.
---

# Playbook Builder

> Imported from a claude.ai iPad session (2026-09-21 handoff) where it lived at
> `/mnt/skills/user/playbook-builder/SKILL.md`. That path is specific to the
> claude.ai skill system and doesn't carry over here — this copy is the
> reference version for anyone (human or Claude) working in this repo. It's a
> *meta*-playbook: the process used to build `rra-phone-sales-launch.md` below.

Converts a job the user does repeatedly into a standalone, reusable Skill Claude can run without re-interviewing every time it's invoked again for the *same* job. A brand-new job still needs its own pass through this process — the content is job-specific — but the user never has to re-explain or re-paste this methodology; just naming the job triggers it.

## When to use this
- User wants to document, systematize, or hand off a repeated task
- User says "turn this into a playbook/skill/SOP"
- User is repeating instructions for something they've asked for before
- User is updating an existing playbook rather than starting fresh (see "Updating vs creating" below)

## Stage 1 — Interview

Ask the user what the job is in one line. Then interview them, **one question at a time**, waiting for each answer. Ask **at least 8 questions** before writing anything, and don't stop until the user says you're done. If the current conversation already contains the answer to a question (e.g. they described the process earlier), skip re-asking it and confirm your extraction instead.

Cover all of these:
1. What triggers the job, and how often
2. The inputs, and exactly where each one lives
3. The steps in the order they actually do them
4. Every decision they make, and the rule behind it
5. What they check before calling it finished
6. Edge cases that have gone wrong before
7. The tone or standard the finished thing has to hit
8. What a bad version looks like

Do not create any files until this interview is complete and the user has confirmed you're done.

## Stage 2 — Write the playbook

Create a folder `[job-name]/` and write `[job-name]/SKILL.md` with these sections:
- **Purpose** (one line)
- **When to use this**
- **Inputs**
- **Steps** (numbered, plain language, no jargon)
- **Decisions** (if X then Y, pulled from interview answers)
- **Definition of done** (see Stage 3)
- **Edge cases**

### Saving reusable files
If the job produces something reusable (a script, template, email, checklist) that will be needed again:
1. Save it to `[job-name]/files/` with a descriptive name (e.g. `numbers-pull.py`, `update-template.md`) — no dates or version numbers in the filename.
2. Turn job-specific specifics into `[placeholders in square brackets]`, and keep one filled-in example underneath as a reference.
3. In SKILL.md, have the relevant step point to the file by name and state when to use it and when not to.
4. Add one line to `[job-name]/files/INDEX.md`: file name, what it's for, today's date.

Never save: one-off outputs, anything containing a password or API key, or a draft the user hasn't approved.

## Stage 3 — Definition of done

Write 5–10 checks specific to this job. Every check must be verifiable with evidence outside your own opinion: a number traced to its source file, a link that loads, a screenshot of the rendered result, a test that runs, a claim matched to a quote, a count, or a value checked against a reference file. No vague quality words (clear, professional, high quality, etc.).

**From then on, every time this playbook runs, before showing the result:**
1. Run every check.
2. Fix what fails.
3. Run them again.
4. Report one line pass/fail per check, with the evidence used.
5. List anything that couldn't be verified, and say why, instead of assuming it passed.

If more than two checks fail on the first pass, stop and report which part of the process caused it rather than patching the output.

## Stage 4 — Close out

Show the user the complete SKILL.md. Ask two questions: what did you get wrong, and what did they forget to tell you. Fold any corrections back into the file before considering it done.

## If files can't be written directly

Never claim a file was saved if it wasn't. Print the complete file contents in the chat, state the exact filename and destination folder, and tell the user to replace the old copy rather than create a duplicate.

## Updating vs. creating

If the user is refining an *existing* playbook rather than starting a new job, skip the full 8-question interview — read the current SKILL.md, ask only what changed, and edit in place.
