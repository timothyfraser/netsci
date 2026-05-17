Create a high-quality flashcard set for a SYSEN 5470 student on the 
topic below. Output a numbered list, one card per entry, copy-pasteable 
into Anki or Quizlet.

FORMAT (every card)
FRONT: [prompt the student sees first]
BACK: [concise, specific, testable answer]
TAG: [VOCAB | FUNCTION | CONCEPT | COMPARE | APPLY | DIAGNOSE]
SOURCE: [specific lab, case study, or glossary entry from the notebook]

COUNT: 12-20 cards. Stop when topic is covered; do not pad.

CARD TYPES — pick the right type for the right knowledge

1. VOCAB — terms a student must recognize and define
   FRONT: single term
   BACK: one-sentence definition + concrete engineered-system example
   EX:
     FRONT: Betweenness centrality
     BACK: How often a node sits on the shortest path between other 
       pairs. A substation with high betweenness is a bottleneck — if 
       it fails, many transmission paths break.
     TAG: VOCAB

2. FUNCTION — code functions a student must recall by name
   FRONT: short task description + 📦 package
   BACK: function call with minimal syntax + one-line note on what it 
     does or returns
   EX:
     FRONT: Activate the nodes table of a tbl_graph so dplyr verbs 
       operate on nodes 📦 tidygraph
     BACK: activate(g, "nodes")
       Returns the same tbl_graph with nodes "active". Subsequent 
       mutate/filter calls operate on nodes until you activate("edges").
     TAG: FUNCTION
   FUNCTION cards always pair task + package, so the student learns 
   "I need X from package Y" rather than rote syntax.

3. CONCEPT — ideas a student must understand and apply
   FRONT: question that tests understanding, not recall
   BACK: 2-3 sentences grounded in an engineering scenario
   EX:
     FRONT: Why does the same network look different under circular vs. 
       force-directed layout, and why does it matter?
     BACK: Both encode identical edges, so analytical measures are the 
       same. But circular layout makes "shortcut" edges visible as 
       chords across a ring; force-directed deforms the ring and hides 
       them. Layout is a rhetorical choice, not a default.
     TAG: CONCEPT

4. COMPARE — distinctions students confuse
   FRONT: "X vs. Y — when do you use each?"
   BACK: one sentence on each + a rule of thumb
   EX:
     FRONT: Degree vs. betweenness centrality — when does each matter?
     BACK: Degree counts direct ties — use for local connectivity 
       (popular hubs). Betweenness counts shortest paths through a 
       node — use for bottlenecks and flow control. A node can be high 
       in one and low in the other.
     TAG: COMPARE

5. APPLY — "what would you do" scenarios
   FRONT: short engineering scenario ending in a question
   BACK: the reasoning path, not just an answer
   EX:
     FRONT: A regional supplier provides 3 of the 5 components your 
       factory uses. Which network analysis would you run first to 
       assess your exposure?
     BACK: Build a bipartite supplier-component network, then take the 
       one-mode projection onto components. The projection reveals 
       components co-affiliated through shared suppliers — a single 
       supplier failure cascades to every component they touch.
     TAG: APPLY

6. DIAGNOSE — error messages and common mistakes (code topics only)
   FRONT: an error message or wrong-output symptom
   BACK: what it usually means + the kind of fix to look for (NOT the 
     specific fix)
   EX:
     FRONT: ggraph error: "Edges should be a valid edge list"
     BACK: Your edge data frame is missing 'from'/'to' columns or 
       they're named differently. Check names(edges) and rename.
     TAG: DIAGNOSE

RULES
- One idea per card. Split if it has two.
- Front must be answerable without the back. No "Explain X" with no 
  context.
- Back must be specific and testable. No vague "it's important..."
- Ground in engineered systems where possible — supply chains, transit, 
  power grids, communication, disaster response.
- FUNCTION cards always include package as 📦 dplyr / 📦 tidygraph / 
  📦 igraph / 📦 ggraph / 📦 broom.
- Never invent functions, definitions, or examples. If topic isn't in 
  notebook sources, say so and stop.

TYPE MIX BY TOPIC
- Pure vocabulary → mostly VOCAB + a few COMPARE
- R/Python package → mostly FUNCTION + a few DIAGNOSE + 1-2 CONCEPT
- Conceptual (e.g. "permutation tests") → mix VOCAB, CONCEPT, COMPARE, 
  APPLY
- Mixed → use relevant types, don't force every type

ORDER: foundational to advanced, learnable top to bottom. Group 
related cards.

GROUNDING: cite specific lab/case study/glossary entry per card. If 
thinly covered, say so and generate fewer cards.

---
TOPIC:
