# SYSEN 5470 Study Companion — Prompt Library

The Study Companion is a NotebookLM-powered tutor for this course. It knows your syllabus, labs, and readings, and it's set up to **help you think — not to hand you answers**.

Below are prompts you can copy-paste into the Study Companion to activate specific study modes. Replace bracketed text like `[Lab X]` with your actual lab number or concept.

**Tip:** The Companion is designed to ask you questions back. That's the point. If it feels like it's not just giving you the answer — it isn't, and that's working as intended.

---

## Group 1: Learn the Vocab

### Flashcards
```
Generate 10 flashcards covering the key vocabulary from [Lab X / Module Y].
Quiz me one at a time: show me the term, wait for my answer, then tell me
whether I was close and what I missed. Keep a running score. At the end,
list the terms I got wrong so I can review them.
```

### Explain like I'm new to this
```
I'm about to read [Lab X]. Before I start, give me a 4-sentence orientation:
what's the core concept, why does it matter for engineered systems, what's
one common misconception, and what should I be drawing on my sketchpad as
I read?
```

---

## Group 2: Debug My Thinking

### Concept check
```
I'm going to explain [concept] in my own words. After I'm done, identify
any gaps or misconceptions — but don't tell me the right answer. Instead,
ask me 2-3 questions that will help me find them myself.

Here's my explanation: [...]
```

### Interpretation coach
```
I ran [analysis] and got [result]. I think it means [my interpretation].
Don't tell me if I'm right. Instead, ask me what else could explain this
result, or what I'd need to check to be more confident in my interpretation.
```

### Error decoder
```
I got this R error: [paste error]
Explain what this category of error usually means conceptually — what
general kind of mistake produces it. Do not reference the specific
variables, function calls, or line numbers in my code. I want to find
the fix in my own code myself.
```

---

## Group 3: Prep for Lab

### Sketchpad warm-up
```
I'm about to start [Lab X]. Before I open R, walk me through 3 questions
I should sketch out by hand. Don't tell me the answers — just give me good
questions that will set up the lab.
```

### Function reconnaissance
```
[Lab X] uses these functions: [list].
For each one, give me a one-sentence description of what it does and what
kind of input/output to expect. Don't write code — just help me know what
to expect when I see them.
```

---

## Group 4: Reflect & Connect

### Post-lab reflection
```
I just finished [Lab X]. Ask me 5 questions about what I observed and what
it means, increasing in difficulty. After each of my answers, tell me one
thing to think harder about — but don't grade me.
```

### Cross-lab connection
```
How does the concept of [X from Lab N] relate to [Y from Lab M]? Don't
just tell me — ask me 2 questions first that help me see the connection
myself, then confirm or extend what I figure out.
```

### Engineer's lens
```
I just learned [concept]. Help me see why this matters for a systems
engineer working on [my domain: e.g. power grid resilience / supply chain /
crisis logistics]. Ask me where I think it applies first, then add what
I missed.
```

---

## Week 1 Orientation Activity (~15 min)

Before you tackle Lab 1, do this once to get familiar with the tool:

1. Pick **one prompt from each of the four groups** above.
2. Try each one with the Study Companion. Use real material from the syllabus or Lab 0/1.
3. Write **one line per prompt** in your sketchpad or reflection log:
   - Did it help?
   - Did it try to just give you the answer?
   - Did you learn something you wouldn't have otherwise?

Bring your reflections to the first synchronous lab session.
