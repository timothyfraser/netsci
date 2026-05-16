# SYSEN 5470 — Network Science for Systems Engineering

_Auto-generated NotebookLM source · 2026-05-16 19:46 UTC_

This document is the concatenated visible text of the course website. It refreshes automatically whenever the site changes. Paste this file into NotebookLM as a source.

---

# SYSEN 5470 · Network Science for Systems Engineering

_Source: docs/index.html_

Skip to content


Cornell Engineering
Summer 2026
3 Credits
Graduate
100% Asynchronous

SYSEN 5470 · June 22 – July 10, 2026


# Network Scienceand Applicationsfor Systems Engineering


Supply chains collapse. Power grids fail. Logistics break down. Engineers who understand networks can see these failures coming — and design systems that survive them. Learn to think in networks in just **3 weeks**.


View Syllabus
Open the Labs


3Weeks · 3 Credits
9Real\-World Case Studies
4Professional Skills
0Coding Experience Required


New here?
## Start with these four steps.


In order. About an hour total if you go slowly. None of it is graded — it's the path of least friction into the rest of the course.


1. 1

Read the syllabus →
Three weeks, eleven labs, four skills. 10 minutes.
2. 2

Set up your environment →
Install R or Python and the course packages. 20–30 minutes.
3. 3

Try the R quickstart →
From zero to your first centrality calculation. 30 minutes. Python version →
4. 4

Open your first lab: Build a Network →
Construct a network from prose. The foundation of everything else.


What You'll Learn

🕸️Network FundamentalsNodes, edges, direction, weighting, small\-world phenomena.
📊Centrality \& CriticalityFind bottlenecks, hubs, and vulnerabilities in any system.
📐Network StatisticsPermutation tests, bootstrap, causal inference on networks.
🚦Routing \& OptimizationSolve real flow and routing problems in logistics and transit.
🧩Clustering \& CommunitiesDetect structure in large\-scale networks automatically.
🤖AI \& Machine LearningNeural networks, graph neural nets, and ML for inference.
🗺️VisualizationCommunicate insight with beautiful, interactive graphics.
🗄️Big Network DataMillions of edges, databases, and smart sampling.


Four Professional Skills
This course doesn't survey network science — it builds four concrete, transferable analytical skills for engineers who work with interdependent systems. Each one is framed against the everyday alternative most engineers reach for first.


🧭IdentifyFrame messy relational data as a graph that answers a real question.
📏MeasureQuantify structure — centrality, betweenness, thresholding.
🔬InferTest claims with permutation against the right null model.
🔮PredictForecast outcomes with embeddings and graph neural networks.


Read the flyer


Case Studies
Nine engineering problems, each one a network underneath. All nine have live interactive labs — eleven labs in total, since AI/ML and Big Data each pair two labs together.


🕸️ Build a Network
📊 Centrality \& Criticality
📐 Network Statistics — Bluebikes
📦 Supply Chain Resilience
🚦 Routing — Lakeside Bikeshare
🧩 Clustering — Design Structure Matrices
🧠 GNN Forward Pass by Hand
🤖 GNN \+ XGBoost — Supplier Risk
🗺️ Visualization — Aggregation
🗄️ Big Data — Sampling
🔗 Big Data — Joins


3 Weeks · 3 Themes


Week 01
#### Think Like a Graph


Jun 22 – Jun 28
* Nodes, edges, directionality, weights
* Small\-world \& scale\-free networks
* Bluebikes mobility case study
* R / Python quickstart labs


Week 02
#### Find What Matters


Jun 29 – Jul 5
* Centrality, criticality, betweenness
* Permutation tests \& null models
* Supply\-chain resilience case study
* Sketchpad lab — draw your own DSM


Week 03
#### Move \& Predict


Jul 6 – Jul 10
* Routing \& flow optimization
* Graph neural networks \+ XGBoost
* Hurricane evacuation case study
* Final visualization mini\-project


How It Works
* 100% asynchronous — learn on your schedule
* Assignments due Monday mornings at 9 AM
* Hands\-on labs in R (Python also welcome)
* Sketchpad exercises — draw networks by hand
* Short videos plus interactive tutorials
* Real datasets from day one
* Designed for full\-time working professionals
* Extensions for SYSEN 5940 in\-person students


Your Instructor

![Tim Fraser headshot](images/instructor.jpg)

### Tim Fraser, PhD


Assistant Teaching Professor · Computational Social Scientist · Systems Engineering Program, Cornell University

 Research on resilience, mobility networks, and computational social science.

→ tmf77@cornell.edu


## Enroll This Summer!


No prior coding or graph theory experience required. Just bring your curiosity — and a sketchpad.


SYSEN 5470
June 22 – July 10, 2026
3 Credits
Asynchronous

Register at Cornell


 Prerequisites: None. Some prior R or Python experience helpful but not required.

**This course is designed for graduate students at all coding levels.**

 Questions? Contact **tmf77@cornell.edu** ·
 Original flyer

---

# Syllabus · SYSEN 5470

_Source: docs/syllabus.html_

Skip to content


SYSEN 5470 · Summer 2026


# Course Syllabus


Three weeks. Nine case studies. Four skills you'll take into your engineering practice. Every unit follows the same six\-slot rhythm so you always know where you are, what's next, and why you're doing it.


The Six\-Slot Unit
Every case study moves through the same six slots — a tested rhythm that respects your time as a full\-time working professional. Video stays under 25%. Coding is the plurality, not the whole.


01 · Frame#### Stakes

What's the engineering problem? Where does the naive approach fail?

\~5–10%
02 · Video#### Concept

Asynchronous lecture covering 3–5 key ideas. Barabási\-anchored.

\~20%
03 · Read#### Anchor

One textbook chapter plus one engineering paper that grounds it.

\~20%
04 · Sketch#### Mental Model

Hand\-drawn activity. No keyboard. Forces the concept into your head.

\~20%
05 · Code#### Lab

R or Python lab — student picks the language. Diagnosis → hypothesis → counterfactual.

\~30%
06 · Check#### Reflect

Embedded multiple\-choice checks plus one interpretation prompt.

\~10%


VIDEO 20%
READ 20%
SKETCH 20%
CODE 30%
CHK 10%


Video
Read
Sketch
Code
Check


Four Professional Skills
Every case study is anchored to one of these four skills. You'll see the naive alternative most engineers reach for first, then the network\-aware approach that earns its keep.


🧭Identify · Frame as a graph**Naive:** spreadsheet joins until something breaks. **Network\-aware:** reachability, dependency queries.
📏Measure · Quantify structure**Naive:** mean and sum. **Network\-aware:** degree, betweenness, eigenvector centrality.
🔬Infer · Test claims**Naive:** vanilla regression on connected observations. **Network\-aware:** permutation tests with the right null.
🔮Predict · Forecast outcomes**Naive:** flat\-feature XGBoost. **Network\-aware:** embeddings, GNNs, neighborhood as feature.


Case Studies · The Nine Units


🕸️

Network Fundamentals — Build a NetworkIdentify
Build networks from prose. Switch directed / undirected, k\=1–4 partitions, force / circular / bipartite layouts — and see canvas, tables, and adjacency matrix all stay in sync.

Open Lab →


📊

Centrality \& Criticality — Riverdale MetroMeasure
Identify bottlenecks, hubs, and vulnerabilities. Remove a station, watch the network reshape — see why a bridge node (low degree, high betweenness) can be more critical than the busiest hub.

Open Lab →


📐

Network Statistics — Bluebikes MobilityInfer
Permutation, jackknife, and bootstrap on networks. Does income shape who rides with whom?

Open Lab →


🚦

Routing \& Optimization — Lakeside BikesharePredict
Counterfactual Monte Carlo on a 15\-station bikeshare. Add a station, build a connector, boost a corridor — and decide whether the improvement is real or just noisy ridership.

Open Lab →


🧩

Clustering \& Communities — Design Structure MatricesMeasure
Reorder rocket, drone, and software DSMs by hand to find modular blocks — then see what Louvain finds and what cross\-cutting components no permutation can fix.

Open Lab →


📦

Supply Chain ResilienceMeasure
Counterfactual node and edge removal. Why the busiest node is rarely the most critical one to protect.

Open Lab →


🧠

AI \& ML · GNN Forward Pass by HandPredict
Hand\-arithmetic walkthrough of a forward pass — plain NN first, then GNN — on a four\-factory supply chain. See exactly where graph structure enters the math.

Open Lab →


🤖

AI \& ML · Supplier Disruption RiskPredict
Graph neural networks, embeddings, and ML for network inference. Static and temporal GNNs. Watch AUC climb as you add neighborhood\-aware features.

Open Lab →


🗺️

Visualization — Aggregation as StrategyIdentify
Bluebikes morning flows at three zoom levels. Watch a clean socioeconomic story emerge as a hairball collapses into a 5×5 matrix.

Open Lab →


🗄️

Big Network Data · Sampling StrategiesIdentify
40\-parish Gulf evacuation network. Pick a sampling strategy and watch which features survive — triangles, degree, geographic coverage.

Open Lab →


🔗

Big Network Data · Joins \& PipelinesIdentify
Drag\-and\-drop pipeline builder in R or Python. Joins, renames, group\-by, summarise — and the column\-collision moment that's the whole reason renames exist in network joins.

Open Lab →


Readings · Primary Texts
The main textbook is Barabási — free online. Selected chapters from Easley \& Kleinberg, Menczer\-Fortunato\-Davis, and applied engineering texts round out each unit.


* Barabási, A.\-L. (2016\). *Network Science.* Cambridge University Press. networksciencebook.com · free online
* Easley, D., \& Kleinberg, J. (2010\). *Networks, Crowds, \& Markets.* Cambridge University Press. PDF · free
* Menczer, F., Fortunato, S., \& Davis, C. A. (2020\). *A First Course in Network Science.* Cambridge University Press. course site
* Bertsekas, D. P. *Network Optimization.* MIT. PDF


Per\-Case\-Study Readings
### 🕸️ Network Fundamentals


* Gladwell, M. (1999\). Six Degrees of Lois Weinberg. *The New Yorker.*
* Barabási, Ch. 1 \& 2\. Intro · Graph Theory
* Easley \& Kleinberg, Ch. 3: Strong and Weak Ties.


### 📊 Centrality \& Criticality


* Barabási, Ch. 3 (Random Networks), Ch. 8 (Robustness), Ch. 10 (Spreading).
* Easley \& Kleinberg, Ch. 3\.6 (Betweenness), Ch. 19 (Cascading Behavior).


### 📐 Network Statistics


* Farine, D. R. (2017\). A guide to null models for animal social network analysis. *Methods Ecol. Evol.* 8: 1309–1320\. DOI


### 🧩 Clustering \& Communities


* Barabási, Ch. 9 (Communities), Ch. 2 (Bipartite Graphs).
* Easley \& Kleinberg, Ch. 4\.3 (Affiliation), Ch. 10 (Matching Markets).


### 🤖 AI \& Machine Learning


* Khan et al. (2025\). Optimizing machine learning for network inference. *Sci Rep* 15, 24472\. DOI
* Resce et al. (2022\). Machine learning prediction of academic collaboration networks. *Sci Rep* 12, 21993\. DOI
* Ding (2025\). A Comprehensive Survey on AI for Complex Networks. *arXiv.* DOI


### 🗺️ Visualization


* Bellantuono et al. (2025\). Analyzing the accessibility of Rome's healthcare services via public transportation. *Sci Rep* 15, 22880\. DOI


## Ready When You Are


The labs are open — you can preview them now. Enrollment opens through Cornell Class Roster.


SYSEN 5470
June 22 – July 10, 2026
3 Credits

Browse the labs


**SYSEN 5470 · Network Science and Applications for Systems Engineering**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Course Materials · SYSEN 5470

_Source: docs/materials.html_

Skip to content


SYSEN 5470 · Course Materials


# What to Bring.


Short list, on purpose. The course leans on hand\-sketching, your own working data, and free open\-source software. Here's what to have on day one — and the one\-page Environment Setup walks you through getting it all installed.


Required


1

### A sketchbook \+ your favorite pens


Any unlined sketchbook is fine — pocket\-size or full\-size, your call. Bring whatever you actually like to draw with: pens, colored pencils, markers, highlighters. The sketch\-before\-code rhythm only works if the tools feel good in your hand.


2

### A camera on hand


Your phone camera is fine. You'll photograph sketch\-pad assignments and upload them as part of weekly submissions, so make sure it's somewhere within arm's reach when you sit down to work.


3

### The Canvas mobile app


Install the Canvas Student app on your phone. The sketch\-pad assignments are much faster to submit straight from your phone (snap → upload → done) than dragging photos through a desktop browser.


Optional but Useful


4

### A Claude Pro subscription Optional


$20 for one month covers the entire course. For a 3\-week intensive, having a strong assistant for nitty\-gritty syntax, debugging, and clarifying questions can save you real hours — especially evenings and weekends when office hours are closed.


Not required, and you can absolutely succeed without it. But if you're going to try one paid subscription for the duration, this is the one we'd suggest. See anthropic.com/pricing.


⚖ AI Use Policy
### What AI is for in this course (and what it isn't).


The short version: AI is welcome for **syntax and debugging**, not for **writing your reports or answering reflections**. The course is about your thinking; reports are how we see your thinking.


#### You may use AI for


* Syntax help and debugging
* Explaining error messages
* Clarifying readings or lab concepts
* Generating example data


#### You may not use AI for


* Writing your project report prose
* Answering Learning Checks
* Writing reflections or interpretation prompts


The **Course Companion** (NotebookLM) is grounded in this course's own materials and is the recommended way to ask AI questions during the course. It will not write your reports for you, by design.


Read the full AI Use Policy →


5

### An editor / IDE Pick one


**Recommended:** Positron — same Posit folks who built RStudio, multi\-language (R \+ Python), AI\-aware. One install, works for both course tracks.


**Other fine choices:** RStudio if you already love it (R only). VS Code \+ Cursor if you live in VS Code already. Whatever you pick, the Environment Setup page walks through installing R or Python and the course packages.


Setup


6

### Set up your environment \~30 min, once


Install Positron (or your editor of choice), then install R or Python and the course packages. The Environment Setup page is a single\-page walkthrough — pick your language, run one install command, run the "hello network" verification snippet. If something fails, the page has the common fixes.


If you can't or don't want to install software locally, the in\-browser Playground runs both R and Python with the course packages pre\-loaded. Every lab works there.


7

### Clone the course repo \~5 min


Once Git is installed, pull down a local copy of the course repository so you can re\-read materials offline and follow along with code:


```
git clone https://github.com/timothyfraser/netsci.git
cd netsci
```

The GitHub Setup page covers the rest — installing Git, making a GitHub account, and creating your own project repo for the three project case studies.


## Questions about Materials?


If you're unsure whether something on (or off) this list applies to you, just ask.


SYSEN 5470
June 22 – July 10, 2026
3 Credits

Email tmf77@cornell.edu


**SYSEN 5470 · Course Materials**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Four Professional Skills · SYSEN 5470

_Source: docs/four-skills.html_

Skip to content


SYSEN 5470 · Network Science for Systems Engineering


# Four Professional SkillsYou'll Take Into Practice.


This course doesn't survey network science — it builds **four concrete, transferable analytical skills** for engineers who work with interdependent systems. Each one is framed against the everyday alternative most engineers reach for first, so you know not just *how* to apply it but *when* it's the right tool.


The Four Skills


Skill 01
*Graph framing* \& data wrangling


 Turn messy relational data — supplier lists, transaction logs, dependency tables — into a **graph that answers a real question**. Recognizing that your problem is a graph problem, then getting enterprise data into nodes and edges, is the skill most engineers are missing.


Instead of
Spreadsheet lookups and joins until something breaks.
You'll do
Structured graph analysis with reachability and dependency queries.


Skill 02
*Network\-aware* inference


 When observations are connected, the **independence assumption fails silently** — and your regression lies to you. Use permutation tests against the right null model to know when a pattern in relational data is real and when it's an artifact of network structure.


Instead of
Vanilla regression on connected observations.
You'll do
Permutation tests against structurally appropriate null models.


Skill 03
*Counterfactual* disruption simulation


 Remove a node. Rewire an edge. Recompute. Repeat ten thousand times. This is how modern supply chain risk firms — Resilinc, Interos, Everstream — actually work, and it's **the skill industry is hiring for right now**. You'll quantify resilience, not estimate it.


Instead of
Point estimates and tabletop "what if" exercises.
You'll do
Monte Carlo node and edge removal with quantified resilience metrics.


Skill 04
*GNN\-based* node outcome prediction


 When you're predicting whether a supplier will fail, a transaction is fraud, or a part is defective, **the neighborhood often carries more signal than the node itself**. Build pipelines that use network structure as a feature — from Node2Vec \+ XGBoost through full graph neural networks.


Instead of
Flat\-feature XGBoost that ignores connectivity.
You'll do
Embedding\- and GNN\-based prediction with network features.


§

 Every lab in this course maps to one of these four skills, and opens with the **naive alternative** most engineers reach for first — so you see exactly where it falls short and why a network\-aware approach earns its keep. You'll graduate with tools that **differentiate you from peers who didn't take this course**, on problems where interdependence is the problem itself.


Try The Skills In The Live Labs

📐 Infer · Bluebikes permutation
📦 Measure · Supply chain
🤖 Predict · GNN \+ XGBoost
🗺️ Identify · Bring your own data


**SYSEN 5470 · Network Science and Applications for Systems Engineering**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Case Studies · SYSEN 5470

_Source: docs/case-studies.html_

Skip to content


SYSEN 5470 · Case Studies


# Nine Problems.One Network Underneath.


Every case study starts with a system that's already broken — supply chains, transit, evacuation, suppliers — and asks you to find what a traditional analysis would miss. Eleven labs are live across nine case studies. Everything is open.


Interactive Labs


🕸️### Build a Network


Identify
Live Lab

A playground for the most fundamental skill in the course: turning a paragraph of prose into a graph. Place nodes, draw edges, switch directed / undirected, flip between manual / force / circular / bipartite layouts, and see the same network as canvas \+ node table \+ edge table \+ adjacency matrix at the same time.


Gladwell · Barabási Ch. 1–2
Open Lab →


📐### Network Statistics


Infer
Live Lab

Does income shape who rides with whom on Boston's Bluebikes? Permutation\-test a mobility network against the right null model — and see why an unblocked permutation lies to you when the system has structure.


Farine 2017 · Barabási Ch. 3
Open Lab →


📦### Supply Chain Resilience


Measure
Live Lab

Remove a node. Rewire an edge. Recompute. Find out why the busiest node in your supply chain is rarely the most critical one to protect — and how degree centrality misleads you when betweenness is the real signal.


Barabási Ch. 8 · E\&K Ch. 19
Open Lab →


📊### Centrality \& Criticality


Measure
Live Lab

Riverdale Metro. Remove Union Terminal vs. remove Ironworks — see why the bridge node (low degree, high betweenness) is more critical to the network than the biggest hub. Click any station, watch APL and components shift in real time.


Barabási Ch. 8 · E\&K Ch. 3\.6
Open Lab →


🧠### GNN by Hand · Forward Pass


Predict
Live Lab

Walk through every arithmetic step of a forward pass — plain NN first, then GNN — on a four\-factory supply chain so small you can check it with a calculator. See exactly where graph structure enters the math.


Khan 2025 · Resce 2022
Open Lab →


🤖### GNN \+ XGBoost · Supplier Risk


Predict
Live Lab

Predict which suppliers will be disrupted next quarter using neighborhood structure as a feature. Watch AUC climb from 0\.71 (raw features only) to 0\.91 (raw \+ temporal GNN embedding \+ lag).


Khan 2025 · Ding 2025
Open Lab →


🚦### Routing \& Optimization


Predict
Live Lab

Lakeside Bikeshare. Predict which proposed intervention — new station, new connector, boosted corridor — actually improves the network. Monte Carlo simulator with Poisson edge\-weight resampling and a 95% CI tells you whether the effect is real or just noise.


Bertsekas · Network Optimization
Open Lab →


🧩### Clustering \& Communities


Measure
Live Lab

Three engineered systems as Design Structure Matrices — rocket, drone, software. Drag rows and columns to chase modular blocks by hand, then watch Louvain do it better. Then ask what the residual off\-block marks are trying to tell you.


Barabási Ch. 9 · E\&K Ch. 4 \& 10
Open Lab →


🗺️### Visualization · Aggregation


Identify
Live Lab

Bluebikes morning\-commute flows at three zoom levels — raw stations, neighborhoods, income quintiles — plus matrix and chord views. Watch a clean socioeconomic story emerge as the hairball collapses into a 5×5 grid. The point isn't pretty graphs; it's *losing detail to gain insight*.


Bellantuono 2025
Open Lab →


🗄️### Big Network Data · Sampling


Identify
Live Lab

A 40\-parish Gulf evacuation network too big to wrangle whole. Pick a sampling strategy (random node, ego, snowball, random edge), watch which features survive — triangles, degree, geographic coverage. The friendship paradox is built into the design.


E\&K Ch. 2\.4
Open Lab →


🔗### Big Data · Network Joins


Identify
Live Lab

Drag\-and\-drop pipeline builder in R (dplyr) *or* Python (pandas) — student picks. Get the origin factory's tier onto every shipment edge, then add the destination's tier, and watch the column\-collision rename step earn its keep. Live result table and Mermaid flowchart.


E\&K Ch. 2\.4 · dplyr / pandas docs
Open Lab →


Bring Your Own Network
When you have your own edgelist and nodelist, the Visualizer lets you upload them and explore on the spot — map your own from/to/weight/time columns, filter by time, switch layouts, and export PNG.


Open the Visualizer


**SYSEN 5470 · Network Science and Applications for Systems Engineering**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Network Aggregation for Visualization · SYSEN 5470

_Source: docs/case-studies/aggregation.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Identify


# Network *Aggregation* for Visualization


When the network is gobbledygook — zoom out.


A raw bike\-share network with 40 stations and hundreds of edges hides more than it reveals. Aggregate up to neighborhoods, then to income quintiles, and watch a clear socioeconomic flow pattern emerge. The lesson: **losing detail can increase insight.**


⚠ Synthetic data — Boston\-flavored but not real Bluebikes records


Raw stations
Neighborhoods
Income quintiles
Matrix view


Heatmap
Chord diagram


📍 **—** nodes
🔗 **—** edges
🚲 **—** rides
🔍 **—** density


### 📊 Aggregation level


Current viewStations
Nodes—
Edges—
Avg edges / node—
Visual clarity—


### 🎨 Legend


### 💡 What am I looking at?


### ✏️Sketchpad Moment


Before switching to the **Income quintiles** view, pause and sketch on your physical sketchpad: what pattern do you *expect* to see in a 5×5 origin\-destination matrix between income quintiles during a morning commute? Where do you think the heaviest flows will go? Draw a 5×5 grid with arrows for the dominant flows you predict. Then check the matrix view and see what the data actually shows.


### 🚲 Top rides (current view)


▶


| From | To | Rides | Origin attr. | Destination attr. |
| --- | --- | --- | --- | --- |


### 📍 Nodes (current view)


▶


| Node | Attribute | Rides out | Rides in | Net flow |
| --- | --- | --- | --- | --- |


## Learning Checks


LC 01
Switch to the **Raw stations** view. Try to answer this just by looking: which neighborhood receives the most morning rides?


AThe Back Bay / Downtown cluster — it has the most stations and the densest connections, so it must receive the most rides.
BI can't actually tell from this view alone — there are too many overlapping edges to count or compare flows reliably.
CCambridge / Kendall — the stations there are largest, so they must be drawing the most riders.


💡 Hint
🔓 Reveal Answer

**Hint:** Don't try to count edges in the raw view — instead, ask yourself *whether you can*. Hover over a few of the heaviest edges and try to mentally aggregate flows by destination. Notice how your eyes have to do work that the visualization isn't doing for you.
**Answer: B.** This is the whole point of the raw view — it's *hairball*. The node sizes encode total activity at that station, but you can't reliably read directional flow at the neighborhood level from a tangle of station\-to\-station edges. A and C both fall for the same trap: assuming visual prominence (cluster size, node size) equals the answer to a directional question it can't answer. The raw view is honest about the data but useless for the question being asked. **The fix is aggregation, not a fancier raw visualization.**


LC 02
Switch to the **Matrix view** and select the **Heatmap**. Look at row totals (rides originating from each quintile) vs. column totals (rides terminating). Which quintile is the largest *net importer* of morning rides?


AQ1 (lowest income) — they receive the most service jobs commuting in from the suburbs.
BQ5 (highest income) — high\-income neighborhoods host the office districts that draw morning commuters from lower\-income origin neighborhoods.
CQ3 (middle income) — middle\-density mixed\-use areas tend to be the largest flow attractors.


💡 Hint
🔓 Reveal Answer

**Hint:** For each quintile *i*, compute (sum of column *i*) − (sum of row *i*). That's net rides arriving minus rides departing. The largest *positive* value identifies the net importer. The chord diagram makes the same comparison if you look at where the thick ribbons terminate.
**Answer: B.** Q5 is the largest net importer — in this synthetic dataset, morning rides flow from lower\-income origin neighborhoods (Q1–Q3\) into the high\-income downtown/Back Bay employment cluster (Q5\). This pattern was completely invisible at the station level: 40 stations × 40 destinations \= 1,600 possible flows, almost all of them drawn as faint overlapping lines. Aggregating to 5 quintiles collapses 1,600 edges into a 5×5 matrix that fits on screen and has interpretable totals. **This is the central trade\-off of aggregation: you lose station\-level granularity, but gain the ability to see the demographic story.**


LC 03
An engineer at the transit agency asks: "Should we always show stakeholders the aggregated views and skip the raw station map?" Which response is the strongest?


AYes — the raw view is gobbledygook and confuses non\-technical stakeholders. Aggregated views are always more honest.
BIt depends on the decision. Each aggregation throws away information and bakes in a worldview (which neighborhood definitions? which quintile cutoffs?). Match the aggregation to the decision: station\-level for capital planning at specific docks, neighborhood for service\-area decisions, quintile for equity analysis.
CNo — only the raw view shows real data. Aggregated views are derived summaries and shouldn't be the primary deliverable.


💡 Hint
🔓 Reveal Answer

**Hint:** Think about who is asking what question. Would a planner deciding where to add a single new dock care about quintile\-level flows? Would an equity analyst care which two specific stations had the highest pair flow? Aggregation is a *match*, not a *universal upgrade*.
**Answer: B.** Aggregation is a deliberate analytic choice, not a presentation upgrade. Every aggregation embeds assumptions — neighborhood boundaries are political, quintile cutoffs depend on the reference population, and chord diagrams emphasize flows over magnitudes. A is wrong because it treats aggregation as universally clearer when it actually *hides* the information needed for station\-level decisions. C is wrong because raw data isn't automatically more truthful — at the station level, the data is real but the *question being asked* (where do morning commuters go?) can't be answered from it without aggregation. The engineering instinct should be: **name the decision first, then choose the aggregation that supports it.**


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Visualization · Network Aggregation for Visualization**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Build a Network · SYSEN 5470

_Source: docs/case-studies/build-a-network.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Identify


# Build a Network: *Identify the Problem*


A network is not a picture of stuff connected to stuff — it's a deliberate choice about what counts as a node, what counts as a tie, and what direction information flows. This playground lets you construct networks from prose, see them as node\-link diagrams, adjacency matrices, and edge tables simultaneously, and compute structural properties as you build. The tool is for verification and computation. The thinking happens on your sketchpad.


### 🧭 How to use this playground


**Three tools, exclusive — pick one at a time:** 🖱 **Select** highlights a node and shows its details, and lets you drag it around when in manual layout. ✏️ **Add Node** drops a node anywhere you click on empty canvas. 🔗 **Add Edge** connects two nodes — click source, then target. 🗑 **Delete** removes the node or edge you click.


**Three representations, one network:** the node\-link diagram, the node and edge tables, and the adjacency matrix are all views of the same data. Edit anywhere and the others update. This is the lab's central concept: *a network is its edge list and its node list.* The picture is just one way to draw them.


**Layouts:** *Manual* lets you drag nodes; *Force\-directed* runs a physics simulation; *Circular* arranges nodes on a ring; *Bipartite / Tripartite / Quadripartite stacks* become available when you switch partition mode to k\=2, 3, or 4 and assign types in the node table.


**Undo your way out of any mistake:** ↶ Undo and ↷ Redo live in the toolbar, or use `Ctrl/Cmd+Z` and `Ctrl/Cmd+Shift+Z`. Up to 50 steps of history are kept.


### ✏️ Sketchpad Moment — do this before touching the tool


**Read this paragraph carefully:**


"The city's emergency operations center (EOC) coordinates response with the fire department, police department, and hospital. The fire chief and police chief exchange text messages directly throughout each shift. During the last storm, the hospital emailed status reports to the EOC every two hours, and the police called the EOC whenever a road was closed. The EOC, in turn, broadcast briefings to all three agencies over a shared radio channel. The fire department posts its dispatch log to a shared portal that the police and EOC read but the hospital does not."
**On your sketchpad, draw this network TWO ways.**


First, as an **undirected** network where an edge means "these two parties communicate at all, in either direction." Then again, as a **directed**, possibly multi\-edge network where each arrow represents one specific channel (call, email, text, radio broadcast, portal post).


Then answer in writing under your drawings: **Who would find the first network more useful, and who would find the second more useful?** Name a specific role — not "decision\-makers" or "managers," but the actual person whose job depends on this view. What is each role trying to figure out, and which version helps them figure it out?


The bigger lesson: a network is a choice about what counts as a tie. The question you are asking determines which version is "right." There is no universally correct answer.


Tool
🖱 Select
✏️ Add Node
🔗 Add Edge
🗑 Delete


Direction
→ Directed
— Undirected


Layout

Manual (drag)
Force\-directed
Circular
Bipartite stack (k\=2\)
Tripartite stack (k\=3\)
Quadripartite grid (k\=4\)


Partition

Unipartite
Bipartite (k\=2\)
Tripartite (k\=3\)
Quadripartite (k\=4\)


Data
⬇ JSON
⬇ CSV
⬆ Import

⌫ Clear


History
↶ Undo
↷ Redo


## 📐 Network Canvas


SELECT TOOL · 0 NODES · 0 EDGES


**SELECT MODE:** click a node to inspect, drag to reposition (manual layout only).


### 📊 Network Metrics


Nodes0
Edges0
Avg degree—
Max degree—
Density—
Components—
Avg path length—


### 🎯 Selected Node


 No node selected. Use 🖱 Select and click a node.


3 VIEWS · 1 NETWORK · LIVE SYNC


### NODE TABLE 0


| ID | Name | Degree |  |
| --- | --- | --- | --- |
| No nodes yet. Click ✏️ Add Node then click the canvas. | | | |


### EDGE TABLE 0


| Source | Target | Weight |  |
| --- | --- | --- | --- |
| No edges yet. Click 🔗 Add Edge then click two nodes. | | | |


### 🔲 ADJACENCY MATRIX — same network, different view. Cell shade \= edge weight. Hover a cell to highlight that edge on the canvas.


### 📝 Learning Checks — Build, then answer


LC 01
An island electricity grid — build it, then read its structure from the adjacency matrix.


 "A small island grid has one main generating station feeding three transmission substations. Substation A feeds three distribution feeders serving the north residential district, the downtown district, and the hospital district. Substation B feeds two feeders serving the south residential district and the industrial zone. Substation C is held in reserve and connects only to Substation A and to the hospital district as a backup path. The hospital district also has a direct backup tie to the south residential feeder."


**Build it**: construct this grid in the canvas. Decide whether to treat it as directed (power flow generation → loads) or undirected (tie line carries either way) — your choice, but be ready to justify it. Then **open the adjacency matrix view above** and inspect the rows and columns.

Looking at the adjacency matrix, which row/column has the most filled cells, and what does the matrix view reveal about that node that the node\-link diagram does not make as obvious?

AThe main generating station's row has the most filled cells, because it powers the entire grid — the matrix simply restates what the node\-link diagram already showed.
BSubstation A and the hospital district both have heavily\-filled rows. The matrix makes their high degree visually equal — they appear equally central by this measure — even though their roles in the system are very different. The matrix view reveals degree at a glance but flattens hierarchy.
CEvery row has roughly the same number of filled cells, because the grid is a balanced radial network.


💡 Hint
🔓 Reveal Answer


**Hint:** count the nodes each node is connected to. Substation A connects to the main generator, three feeders, and Substation C — that's 5\. The hospital district connects to its feeder from Substation A, Substation C as backup, and the south residential feeder — that's 3\. Now check the avg\-degree metric panel: average is fine, but the matrix view shows you each node's degree visually, just by row/column density.


**Answer: B.** The matrix's strength is that *row sum \= degree* — heavy rows scream "high degree" regardless of how the node\-link layout positioned them. Substation A is the highest\-degree node here (typically 5 ties), and the hospital district is also high (3 ties) because of the dual backup arrangement. The matrix view makes that visible at a glance — but it loses the system hierarchy. A radial diagram clearly shows that Substation A is upstream of three feeders, while the matrix treats all 5 of its ties as equivalent. This is the key lesson: **different representations make different structural properties visible.** Average degree is a one\-number summary; the matrix is a per\-node summary; the node\-link is a hierarchy/topology summary. Each one hides what the others show.


LC 02
A small\-world transportation network — see how layout choice changes what you notice.


 "Six neighborhoods in a small city are each connected to their two nearest neighbors by local roads, forming a ring: Northgate — Eastside — Riverside — Southpark — Westend — Hillcrest — back to Northgate. In addition, the city operates three express bus lines that act as shortcuts: one connects Northgate directly to Southpark, one connects Eastside to Westend, and one connects Riverside to Hillcrest."


**Build it** as an undirected network with 6 nodes and 9 edges. Now view the network under three layouts in sequence: **Circular**, **Force\-directed**, and **Manual** (where you drag nodes yourself to whatever arrangement makes sense to you). Look at the "Avg path length" metric — it stays the same across layouts, because the network is the same.

Under which layout are the three express\-line "shortcuts" most clearly visible as shortcuts — and what does this teach you about layout choice when communicating a network?

AForce\-directed makes the shortcuts most obvious, because the physics pulls connected nodes together and the long edges naturally cross the layout — it's the most accurate visualization.
BCircular makes the shortcuts most obvious as *shortcuts* — the ring of local roads becomes the visible perimeter and the express lines cut across the circle, making their "shortcut" role obvious. Force\-directed actually hides this structure because it deforms the ring to accommodate the cross\-ties. **Layout choice is a rhetorical decision.**
CIt doesn't matter — the network's average path length is the same under any layout, so the layouts are equivalent for analysis purposes.


💡 Hint
🔓 Reveal Answer


**Hint:** the question is not which layout is most "accurate" — they all encode the same edges. The question is which layout makes the *concept of "shortcut"* visually obvious. A shortcut is meaningful only when there is a longer alternative path. Where does the longer alternative show itself most clearly?


**Answer: B.** Under circular layout, the local\-road ring becomes the literal circumference, and the three express lines visibly chord across the circle. You can *see* that each express line skips three nodes of local roads. Under force\-directed, the simulation balances forces in a way that often disrupts the ring — Northgate gets pulled toward Southpark by their shortcut edge, the ring buckles, and the "shortcut\-ness" disappears because it no longer looks like a shortcut against any visible alternative. C is wrong because it conflates analytical equivalence with communicative equivalence. The underlying graph is the same; **the story it tells is not.** This is course outcome \#2 (communicate insights) in action: layout is a choice, not a default. (Note: this network is the classic Watts\-Strogatz small\-world setup in miniature. Average path length here is about 1\.7\. If you delete the three express lines and recompute, it jumps to roughly 1\.8 → reduced to 1\.7 is small for n\=6 but the effect grows dramatically with network size.)


LC 03
A supply chain — only readable once you tell the tool it's bipartite.


 "A regional electronics manufacturer sources from three suppliers. Supplier A provides capacitors and resistors. Supplier B provides circuit boards and capacitors. Supplier C provides displays, circuit boards, and connectors."


**Build it**: 7 nodes total (3 suppliers \+ 4 components) and 7 edges connecting suppliers to the components they provide. Start in **Unipartite** mode and Force\-directed layout. Notice that even though you, the human, know suppliers and components are different kinds of things, the network treats them as one kind. Now switch **Partition** mode to **Bipartite (k\=2\)** — a Type column appears in the node table. Assign each supplier type 0 and each component type 1\. Then change **Layout** to **Bipartite stack**. The network re\-organizes itself.

Pick the component with only one supplier (your single point of failure). Looking at the bipartite layout, how many *other components* are second\-degree neighbors of that critical component — i.e., other components that share at least one supplier with it?

AZero — the critical component is isolated since it has only one supplier.
BOne. Connectors is the single\-supplier component (Supplier C only). Following the two\-step path connectors → Supplier C → {circuit boards, displays} reveals that connectors shares supplier C with two other components — circuit boards and displays — making 2 second\-degree neighbors.
CTwo — connectors is the single\-supplier component, and via Supplier C it shares a supplier with circuit boards and displays. Those are its second\-degree neighbors. This means a disruption to Supplier C affects connectors AND its two coaffiliated components — the single point of failure cascades to three components, not one.


💡 Hint
🔓 Reveal Answer


**Hint:** a second\-degree neighbor in a bipartite network is reached by going through one intermediary — component → supplier → another component. Identify the single\-supplier component first: which component appears in only one supplier's list? Then trace through its supplier to see which other components that supplier also feeds.


**Answer: C.** Connectors has only one supplier (Supplier C). Supplier C also provides displays and circuit boards. So the two\-step neighbors of connectors are {circuit boards, displays} — two components. The systems\-engineering interpretation: a disruption to Supplier C does not just take out connectors; it cascades to circuit boards and displays as well. This is called the *one\-mode projection* of a bipartite network — and it's why bipartite analysis is essential for supply\-chain risk: the apparent single\-supplier\-single\-component vulnerability is actually a multi\-component vulnerability when you account for shared suppliers. The bipartite stack layout makes this visible because it cleanly separates the two node types — in unipartite force\-directed view, suppliers and components mix together and the two\-hop structure is much harder to trace. **The layout is not just decoration — it's the analytic frame that makes the question answerable.**


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Network Fundamentals · Build\-a\-Network Playground**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Centrality & Criticality · SYSEN 5470

_Source: docs/case-studies/centrality.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Measure


# Why Does *Betweenness* Matter?


Explore how removing a single transit station reshapes the entire network — and why the most dangerous node isn't always the biggest one. Click any station to inspect; remove it and watch the metrics shift.


### 🚇 Riverdale Metro \& Bus Network


 **18** active
 **0** removed


### 🔍 Selected Node


🖱️
 Click any station to inspect its centrality metrics


➖ Remove Station
✕ Deselect


### 📊 Network Metrics


🔗 Active Nodes
18


↗️ Avg Path Length
—


📏 Network Diameter
—


🧩 Components
—


🔄 Restore All Stations


### 🗺️ Legend


 **Major Hub** — high degree \& betweenness
 **Bridge** — low degree, high betweenness
 Regular station
 Removed station


---


 Node size \= **degree centrality**

 Node color \= **betweenness rank**


### 📋 Raw Data


Node List
Edge List


| Station | Zone | Degree | Betweenness | Type | Status |
| --- | --- | --- | --- | --- | --- |


| From | To | Line | Weight (riders) |
| --- | --- | --- | --- |


LC 01
Union Terminal has the highest degree in this network — the most direct connections. Does it also have the highest betweenness centrality?


A Yes — highest degree always means highest betweenness, since more connections mean more shortest paths go through you.
B Yes in this case — Union Terminal is both the biggest hub and the highest betweenness node, but that's not always true in other networks.
C No — Ironworks has higher betweenness than Union Terminal, despite having fewer direct connections, because it sits between two clusters that would otherwise be disconnected.


💡 Hint
🔓 Reveal Answer


**Hint:** Look at the color\-coding. Which node is teal (bridge color)? Now check: how many direct neighbors does it have vs. Union Terminal? Then try removing *each one* and watch what happens to the number of connected components.


 ✅ **Answer: C.** Ironworks sits on the narrow corridor connecting the downtown cluster to the northern suburbs. Even though Union Terminal has more direct connections (higher degree), Ironworks has higher betweenness because nearly every shortest path between downtown and the suburbs must pass through it. Degree counts neighbors; betweenness counts how many *other pairs* depend on you.


LC 02
Try removing **Union Terminal** from the network. Then restore it and remove **Ironworks** instead. Which removal causes the number of *connected components* to increase?


A Removing Union Terminal breaks the network into more components, because it has the most connections.
B Removing Ironworks breaks the network into more components, because it's the only path connecting two otherwise separate clusters.
C Both removals break the network into the same number of components, since both are important nodes.


💡 Hint
🔓 Reveal Answer


**Hint:** Actually try it. Click Union Terminal → Remove → check Components. Then reset, click Ironworks → Remove → check again. Pay attention to whether 🧩 Components goes from 1 to 2 (or higher).


 ✅ **Answer: B.** Removing Ironworks disconnects the northern suburbs from the rest of the network — the Components metric jumps from 1 to 2\. Removing Union Terminal increases average path length and raises the diameter significantly, but the network stays connected because the remaining stations can still reach each other via alternate routes. The core insight: *a high\-betweenness bridge node can be structurally more critical than a high\-degree hub.*


LC 03
After removing Ironworks (and the network splits into 2 components), what happens to the *average path length* metric?


A Average path length increases by a small amount, since a few paths are now longer.
B Average path length becomes undefined / infinite, because some node pairs can no longer reach each other at all.
C Average path length decreases, because the two smaller components are individually more compact than the full network.


💡 Hint
🔓 Reveal Answer


**Hint:** Think about what "average path length" means: the average shortest path between *all pairs* of nodes. If two nodes are in disconnected components, what is the "distance" between them? How does that affect the average? Check the metric display.


 ✅ **Answer: B.** When the network disconnects, the shortest path between a node in Component 1 and a node in Component 2 is theoretically infinite (there is no path). The tool displays this as "∞ (disconnected)". This is why *network efficiency* (1 / average path length) collapses to zero when even one bridge node is removed — a common measure in infrastructure resilience analysis. In a supply chain or power grid, this means goods or power can no longer reach certain destinations at all.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Centrality \& Criticality · Interactive Lab**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Counterfactual Monte Carlo · Lakeside Bikeshare · SYSEN 5470

_Source: docs/case-studies/counterfactual.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Predict


# Counterfactual *Monte Carlo* Simulator


Lakeside is a fictional city of 15 bikeshare stations. Planners are debating a network change. Use Monte Carlo simulation to test whether one proposed intervention *significantly* improves the network — or just happens to look good on one noisy dataset.


## The problem an engineer is solving


You are an analyst at the Lakeside Department of Transportation. The current bikeshare network has known weaknesses — some stations are barely connected, some corridors are overloaded. A planner proposes a change: add a station, build a connector, or boost capacity on a route.


Before millions of dollars are committed, the obvious question is: **does this change actually help?** And the harder follow\-up: **how confident are we?**


The ridership counts on each edge are *observed*, but they're noisy. A pair of stations that saw 47 trips last quarter might see 30 or 65 next quarter just from normal variation. A point estimate of network improvement could just be noise.


## The Monte Carlo logic


The simulator below runs the following procedure:


1. For each of N replicates, resample every edge weight from a Poisson distribution whose mean is the original observed weight.
2. On each replicate, compute the chosen metric — both for the **baseline** network and for the **treated** network (after applying the proposed change).
3. Stack all N baseline values into one distribution, and all N treated values into another.
4. Compute the mean and 95% confidence interval of the *difference* between treated and baseline.
5. Decide: does the confidence interval clearly exclude zero? If yes, the change has a statistically meaningful effect at this sample size.


**✏️ Sketchpad — before you click anything**
 Look at the Lakeside map below. By eye, predict which of the three proposed treatments will produce the largest improvement in average path length. Draw the treatment on paper, mark which nodes you think will benefit, and note your prediction. We will return to it.


 **15** stations
 Treatment: **none**
Zones: downtown · campus · waterfront


### Network Legend


 Hub stations (high traffic, high degree)
 Bridge stations (sparse but structurally critical)
 Normal stations
 Proposed new station / edge (when treatment selected)

Edge thickness \= ridership (log scale of observed weight)


### Simulation Controls


Metric of interest


Avg path length (weighted)
Worst\-served node distance
Network diameter
Bottleneck flow (campus\_n ↔ riverwalk)


Avg distance from Market Sq
Weighted degree of Market Sq


Avg distance from Campus N
Weighted degree of Campus N


Avg distance from Boardwalk
Weighted degree of Boardwalk


Proposed treatment

None — baseline only
Add station: Lake Bridge (links waterfront ↔ campus)
Add station: East Gap (links downtown ↔ campus east)
Add station: North Park (north of downtown)
Build connector: market\_sq ↔ harbor\_view
Boost capacity: campus\_n ↔ riverwalk (3× weight)


Monte Carlo replicates (N)


50**500**2000


Run Monte Carlo simulation


Clear results


### Observed Network (Point Estimate)


Stations
—


Edges
—


Total observed trips
—


Avg path length
—


### Monte Carlo Distribution


📊
 Configure a treatment and click **Run Monte Carlo simulation** to see the distribution.


### Effect Size


—
awaiting simulation


### 95% Confidence Interval


—
awaiting simulation


### Statistical Verdict


—
awaiting simulation


## Learning Checks


LC 01
Run the baseline (treatment \= none) with N \= 500 and the metric "Avg path length (weighted)." Then change the metric to "Worst\-served node distance" and run again. Why does the *spread* (width of the histogram) of the worst\-served metric tend to be larger?


ABecause worst\-served distance is computed on more edges, so any noise compounds more.
BBecause it depends on a single node's longest path — a metric driven by extremes is more sensitive to edge\-weight noise than an average over all node pairs.
CBecause Poisson noise grows linearly with edge weight, so heavy edges dominate the worst\-served metric.


💡 Hint
🔓 Reveal answer


**Hint:** Think about how each metric is constructed. Average path length pools information across many pairs, so noise averages out. The worst\-served metric reports a single value — the most extreme one. What happens to extremes when you add random noise to inputs?


**Correct: B.** Averages are stable because random fluctuations cancel out across many pairs. Maximums (or near\-maximums, like the worst\-served station) are unstable because a single noisy edge can change which node is "worst." This is the same reason min/max values in any sample are more variable than the mean — and it has real engineering consequences: equity\-focused metrics inherently demand more data to detect effects with confidence.


**Why not A:** The worst\-served metric uses the same edges as the average; the issue is the function applied to those edges, not the number of edges.

**Why not C:** Poisson *variance* grows linearly with the mean (variance \= mean), but *standard deviation* grows with the square root, so heavy edges are relatively more stable, not less.


LC 02
Set the metric to "Avg path length (weighted)" and compare two treatments by running them separately: "Add station: Lake Bridge" and "Add station: North Park." Which treatment is the better recommendation, and what's the most defensible reason?


ANorth Park, because adding a station in a populated area is generally a good policy.
BLake Bridge, because the point\-estimate effect size is larger.
CLake Bridge, because its 95% CI clearly excludes zero while North Park's CI does not — the effect is statistically distinguishable from a noisy null.


💡 Hint
🔓 Reveal answer


**Hint:** Don't just compare the means — look at the confidence intervals. A larger mean improvement only matters if you can distinguish it from zero. Which treatment gives you a CI that clearly doesn't cross zero?


**Correct: C.** Lake Bridge connects two zones (campus and waterfront) that were previously linked only through the downtown bottleneck — the structural improvement is large and consistent across the Monte Carlo samples. North Park sits adjacent to the already well\-connected downtown core, so its additional edges shave little off the average path length, and the small improvement is within noise.


**Why not A:** Policy intuition is fine for hypothesis generation, but it doesn't tell a planner whether the change is statistically defensible. That's the whole point of running the simulation.

**Why not B:** Point estimates without uncertainty are misleading. A larger mean with a wide CI can be statistically indistinguishable from a smaller mean with a tight CI.


LC 03
Suppose you ran the same simulation at N \= 50 instead of N \= 500\. The treatment effect looks "non\-significant" at N \= 50 but "significant" at N \= 500\. What is the right interpretation?


AThe treatment is more effective when applied to a larger sample of replicates.
BThe effect size doesn't change with N, but the precision of our estimate does — more replicates narrow the confidence interval, so a small real effect becomes detectable.
CN \= 50 is unreliable; the result at N \= 500 is the truth.


💡 Hint
🔓 Reveal answer


**Hint:** Try it. Run the same treatment at N \= 50 a few times, then at N \= 500 a few times. Does the *mean* change much, or just the width of the CI? What does that imply about what increasing N actually does?


**Correct: B.** The true effect size of a treatment is a property of the network and the noise model — N doesn't change it. What N changes is your *estimate's precision*. At small N, sampling noise inflates the CI; at large N, the CI shrinks (proportional to 1/√N). A real, small effect can fail to be detected at low N simply because the CI is too wide. This is the engineering version of statistical power — it tells you how much simulation effort you need to detect effects of a given size.


**Why not A:** The treatment isn't doing more work with more replicates — you're just looking at it through a sharper lens.

**Why not C:** Neither N is "the truth." Both estimate the same underlying effect; N \= 500 just estimates it with less uncertainty.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Routing \& Optimization · Counterfactual Monte Carlo Lab**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# DSM Clustering & Dependency Propagation · SYSEN 5470

_Source: docs/case-studies/dsm-clustering.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Measure


# Design Structure Matrices: *Dependency \& Clustering*


A DSM is the adjacency matrix of a directed dependency graph. Trace cascading failures, then try to reorder the matrix into modular blocks by hand — and discover why clustering algorithms exist.


### ✏️ Sketchpad — do this before you touch the matrix


Draw the system you don't see
1. **Pick one of the three systems below** (rocket, drone, software). Without looking at the matrix, sketch the system as a node\-link diagram on your sketchpad: list 8–15 components and draw arrows for what depends on what.
2. **Now draw a blank 8×8 grid** with your components as both row and column labels. Fill in cells for dependencies you think exist. This is your *predicted DSM*.
3. **Load the actual DSM** and compare. Count: how many real dependencies did you miss? How many did you imagine that aren't there?
4. **Reflect:** Node\-link diagrams hide coupling. Matrices expose it. Which view would you use to convince a program manager that the system is over\-coupled?


🚀Rocket


🛩️Drone Remote Sensing


💻Software Architecture


## Rocket Launch Vehicle


A tightly\-coupled hardware system. Cell (i,j) filled means **row i depends on column j**. Drag row or column labels to reorder. Click any cell or label to inspect that component's failure cascade.


⚡ Cluster Automatically (Louvain)
Show Block Boundaries
Reset to Original Order
Clear Cascade


 **—** components
 **—** dependencies
 **0** in current cascade


### Selected Component


🎯
 Click any row label, column label, or cell to inspect a component and trace its failure cascade.


### Live Metrics


📦 Components—
🔗 Dependencies—
📊 Coupling Density—
🧩 Clusters Found—
⚠️ Off\-Block Marks—
💥 Largest Cascade—


### Legend


 Dependency exists (row depends on column)
 No dependency
 Diagonal (self)
 Cascade source (selected)
 Affected by cascade
 Cluster boundary


### How to Read This


**Rows \= dependents.** If row *i* has a mark in column *j*, component *i* needs *j* to function.


**Marks near the diagonal** \= within\-module coupling (good). **Marks far from the diagonal** \= cross\-module coupling (the things clustering tries to minimize).


**Symmetric permutation:** when you drag a row, the matching column moves with it. This preserves the meaning of the matrix.


## Learning Checks — answer all three before moving on


LC 01 · DIRECT OBSERVATION
### Failure cascades depend on the column, not the row.


Switch to the **rocket** system. Click on the **Electrical Power System** row or column label to highlight its forward failure cascade (everything that would be affected if power failed). How many components are in the cascade (not counting the power system itself)?


A.3–5 components — a localized failure
B.6–9 components — a partial cascade affecting one subsystem
C.10 or more — a system\-wide cascade because power is cross\-cutting


💡 Hint
✓ Reveal Answer


**Hint:** Click the row label "Electrical Power" on the rocket DSM. The matrix will highlight the source in amber and every transitively dependent component in orange. Read the "in current cascade" count from the status bar.


**Answer: C.** Electrical power feeds avionics, GNC, comms, thermal control, payload electronics, and ignition systems — and each of those feeds further components. The cascade typically exceeds 10 components on the rocket DSM. This is the engineering meaning of a *cross\-cutting concern*: power isn't a module, it's an axis. Option A reflects the common intuition that "a subsystem failure stays in its subsystem" — DSMs exist precisely because that intuition is wrong on tightly coupled hardware.


LC 02 · INTERVENTION
### Manual reordering vs. the algorithm.


Switch to the **drone remote sensing** system. Spend 3–5 minutes manually dragging rows and columns to push marks toward the diagonal — try to minimize the "Off\-Block Marks" metric in the sidebar. Then click **Cluster Automatically**. What did you find?


A.My manual ordering was about as good as the algorithm — the structure was visually obvious.
B.The algorithm found roughly the same modules I did, but converged faster and with fewer off\-block marks.
C.Even on \~18 components, manual reordering is genuinely hard — and the algorithm found block structure I missed entirely.


💡 Hint
✓ Reveal Answer


**Hint:** Watch the "Off\-Block Marks" and "Clusters Found" metrics as you drag. Compare your best score to the algorithm's score after clicking Cluster Automatically. Also: did you discover the same three modules (flight stack / payload / ground stack), or something different?


**Answer: C (most students).** The drone DSM has roughly three modules — flight control, sensor/payload, ground/mission — but several bridging components (the gimbal and telemetry radio) belong to two modules at once. Manual reordering quickly becomes a local\-minimum problem: every swap that improves one pair of modules makes a different pair worse. Louvain optimizes modularity globally and routinely finds groupings humans miss. If you answered B, your manual reordering was unusually good — but you almost certainly didn't beat the algorithm's off\-block count. *This is the lab's main point: clustering algorithms exist because the search space is combinatorially huge even for small N.*


LC 03 · CONCEPT TRANSFER
### Why doesn't clustering fix every system?


Run **Cluster Automatically** on all three systems and compare the proportion of off\-block marks (off\-block ÷ total dependencies) in each. Which system has the **highest residual off\-block fraction** even after optimal clustering, and what does that tell you?


A.The rocket — tight physical coupling between propulsion, thermal, and structures creates feedback loops that no permutation can untangle.
B.The drone — mixing hardware and software means the modules don't decompose cleanly.
C.The software architecture — even though it's cleanly layered, its cross\-cutting services (auth, logging, monitoring) touch every module by design and cannot be assigned to a single block.


💡 Hint
✓ Reveal Answer


**Hint:** After auto\-clustering each system, divide "Off\-Block Marks" by "Dependencies" to get the off\-block fraction. Then look at *which* components in the worst system have dependencies crossing cluster boundaries. Do they share something in common?


**Answer: C.** After clustering, the rocket retains roughly 43% of marks off\-block, the drone about 25%, and the software architecture about 56% — the highest of the three. The reason is instructive: the rocket's coupling is dense but *regional* (propulsion talks to propulsion, electrical to electrical), so Louvain finds tight blocks. The software DSM is cleanly layered, but components like **auth, logging, monitoring, and secrets** are *cross\-cutting concerns* — by design, every service depends on them. No reordering can fix this, because the dependencies are real and intentional. *This is the systems\-engineering punchline:* high residual off\-block marks aren't always a sign that the system is badly designed. Sometimes the network is telling you that certain components are **structurally cross\-cutting** — the matrix equivalent of a "bridge" node — and you need a different architectural pattern (aspect\-oriented programming, service mesh, sidecars) rather than more clustering. Option A is the intuitive answer but underestimates how well Louvain handles regional coupling. Option B confuses domain heterogeneity with structural coupling — mixing hardware and software doesn't itself prevent decomposition.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Clustering \& Communities · DSM Lab**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# GNN by Hand · Forward Pass · SYSEN 5470

_Source: docs/case-studies/gnn-by-hand.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Predict


# Neural Networks by *Hand*


Walk through every arithmetic step of a forward pass — first as a plain neural network, then as a graph neural network — on a four\-node supply chain so tiny you can check everything with a calculator.


## 🏭 The Supply Chain


Four factories in a regional supply chain. Each factory has one feature: its **average daily output** (normalized 0–1\). We want to predict whether each factory is a **bottleneck risk** (1 \= yes, 0 \= no).


We have ground\-truth labels from last year's disruption data. The network edges represent **direct material dependencies** — Factory A ships to Factory C, for instance.


■ A
 ■ B
 ■ C
 ■ D
   \|
 Feature x \= normalized daily output  \|   Edges \= material dependency


Setup
### Our data: features and ground\-truth labels


| Factory | Input feature x | True label y (bottleneck?) | Neighbors (ships to) |
| --- | --- | --- | --- |
| A | 0\.8 | 1 (yes) | B, C |
| B | 0\.3 | 0 (no) | D |
| C | 0\.6 | 0 (no) | D |
| D | 0\.9 | 1 (yes) | — |


**Starter weights (random, chosen for easy arithmetic):**

 One hidden neuron, one output neuron. Three weights total:

**w₁ \= 0\.5** (input → hidden),
 **w₂ \= 0\.4** (hidden → output),
 **b \= 0\.1** (bias on hidden neuron).

 ReLU on the hidden layer, Sigmoid on the output.


Part 1
## Plain Neural Network — *no graph structure*


 A standard neural network treats each node as an independent row in a table. It cannot see the edges. We'll run each factory through the same tiny network — one hidden neuron, one output — and compute a bottleneck prediction.


Step 1### Compute the hidden neuron's weighted sum z for each factory


The formula for a single neuron's pre\-activation sum is:


z \= w₁ · x \+ b
 \= (input weight) × (factory's feature) \+ (bias)
\= 0\.5 × x \+ 0\.1
Apply this to all four factories:


z\_A \= 0\.5 × 0\.8 \+ 0\.1 \= 0\.40 \+ 0\.10 \= 0\.50
z\_B \= 0\.5 × 0\.3 \+ 0\.1 \= 0\.15 \+ 0\.10 \= 0\.25
z\_C \= 0\.5 × 0\.6 \+ 0\.1 \= 0\.30 \+ 0\.10 \= 0\.40
z\_D \= 0\.5 × 0\.9 \+ 0\.1 \= 0\.45 \+ 0\.10 \= 0\.55


LC 01Weighted sum

If we added a fifth factory E with x \= 0\.0 (completely offline), what would z\_E be?


A z\_E \= 0\.0, because the feature is zero
B z\_E \= 0\.1, because the bias still adds even when x \= 0
C z\_E \= −0\.1, because the weights pull it negative


Hint
Reveal Answer

💡 Plug x \= 0 into the formula z \= 0\.5 × x \+ 0\.1 and evaluate each term separately.
**B is correct.** z \= 0\.5 × 0 \+ 0\.1 \= 0 \+ 0\.1 \= 0\.1\. The bias term b \= 0\.1 fires regardless of the input — it's a baseline shift. A is wrong because it ignores the bias. C is wrong because no negative weights are in play here.


Step 2### Apply the ReLU activation to get hidden layer output h


ReLU is `max(0, z)` — it passes positive values through unchanged and kills negative ones.


h \= ReLU(z) \= max(0, z)

h\_A \= max(0, 0\.50) \= 0\.50
h\_B \= max(0, 0\.25) \= 0\.25
h\_C \= max(0, 0\.40) \= 0\.40
h\_D \= max(0, 0\.55) \= 0\.55

**Why ReLU?** All z values here happen to be positive, so ReLU passes them through unchanged. But if a neuron got a negative z — say from a large negative weight — ReLU would zero it out, effectively "switching that neuron off." This is what lets deep networks ignore irrelevant patterns.


Step 3### Compute the output neuron: apply w₂, then Sigmoid


The output neuron multiplies the hidden output by w₂, then passes it through Sigmoid to squash it to a probability between 0 and 1\.


output\_raw \= w₂ · h ← no bias on output neuron here

ŷ \= σ(output\_raw) \= 1 / (1 \+ e^(−output\_raw))

── Factory A ──────────────────────────────────
output\_raw\_A \= 0\.4 × 0\.50 \= 0\.20
ŷ\_A \= 1 / (1 \+ e^(−0\.20\)) \= 1 / (1 \+ 0\.819\) \= 0\.550
── Factory B ──────────────────────────────────
output\_raw\_B \= 0\.4 × 0\.25 \= 0\.10
ŷ\_B \= 1 / (1 \+ e^(−0\.10\)) \= 1 / (1 \+ 0\.905\) \= 0\.525
── Factory C ──────────────────────────────────
output\_raw\_C \= 0\.4 × 0\.40 \= 0\.16
ŷ\_C \= 1 / (1 \+ e^(−0\.16\)) \= 1 / (1 \+ 0\.852\) \= 0\.540
── Factory D ──────────────────────────────────
output\_raw\_D \= 0\.4 × 0\.55 \= 0\.22
ŷ\_D \= 1 / (1 \+ e^(−0\.22\)) \= 1 / (1 \+ 0\.803\) \= 0\.555


LC 02Sigmoid intuition

All four predictions are clustered around 0\.53\. Why are they so similar, and so close to 0\.5?


A Because the features are all similar values
B Because the sigmoid function is broken for small inputs
C Because the weights are small and random — the network hasn't learned anything yet


Hint
Reveal Answer

💡 Sigmoid(0\) \= exactly 0\.5\. What happens to the sigmoid output when its input is a small positive number close to zero?
**C is correct.** Our small, random starter weights produce tiny output\_raw values (0\.10–0\.22\), and σ(small number ≈ 0\) ≈ 0\.5\. The network is essentially guessing 50/50 — it hasn't learned yet. Training will push the weights in directions that separate predictions for bottlenecks vs. non\-bottlenecks.


Step 4### Compute Mean Absolute Error (MAE)


MAE measures how wrong our predictions are on average. For each node, we compute \|ŷ − y\|, then average across all nodes.


MAE \= (1/N) × Σ \|ŷᵢ − yᵢ\|

── Errors per node ────────────────────────────
\|ŷ\_A − y\_A\| \= \|0\.550 − 1\| \= 0\.450 ← predicted 0\.55, truth is 1
\|ŷ\_B − y\_B\| \= \|0\.525 − 0\| \= 0\.525 ← predicted 0\.53, truth is 0
\|ŷ\_C − y\_C\| \= \|0\.540 − 0\| \= 0\.540 ← predicted 0\.54, truth is 0
\|ŷ\_D − y\_D\| \= \|0\.555 − 1\| \= 0\.445 ← predicted 0\.56, truth is 1
── Average ─────────────────────────────────────
MAE \= (0\.450 \+ 0\.525 \+ 0\.540 \+ 0\.445\) / 4
 \= 1\.960 / 4
 \= 0\.490

**MAE \= 0\.490\.** That's nearly as bad as random guessing. On a 0/1 classification problem, a perfectly random model averages MAE ≈ 0\.5\. Our untrained network is barely better than a coin flip — expected, since the weights are random. Training will reduce this.


Step 5### Nudge one weight — does MAE go down?


Training is the process of nudging weights to reduce MAE. Let's demonstrate by manually increasing **w₁ from 0\.5 → 0\.9** and recomputing everything.


Intuition: our bottleneck nodes (A and D) both have high x values (0\.8 and 0\.9\). A larger w₁ will amplify high\-x signals and push their predictions closer to 1\.


── New w₁ \= 0\.9, w₂ \= 0\.4, b \= 0\.1 (unchanged) ──

z\_A \= 0\.9 × 0\.8 \+ 0\.1 \= 0\.72 \+ 0\.1 \= 0\.82
z\_B \= 0\.9 × 0\.3 \+ 0\.1 \= 0\.27 \+ 0\.1 \= 0\.37
z\_C \= 0\.9 × 0\.6 \+ 0\.1 \= 0\.54 \+ 0\.1 \= 0\.64
z\_D \= 0\.9 × 0\.9 \+ 0\.1 \= 0\.81 \+ 0\.1 \= 0\.91

h \= ReLU(z) → same values (all positive, pass through)

output\_raw\_A \= 0\.4 × 0\.82 \= 0\.328
output\_raw\_B \= 0\.4 × 0\.37 \= 0\.148
output\_raw\_C \= 0\.4 × 0\.64 \= 0\.256
output\_raw\_D \= 0\.4 × 0\.91 \= 0\.364

ŷ\_A \= σ(0\.328\) \= 0\.581
ŷ\_B \= σ(0\.148\) \= 0\.537
ŷ\_C \= σ(0\.256\) \= 0\.564
ŷ\_D \= σ(0\.364\) \= 0\.590
── New MAE ─────────────────────────────────────
\|0\.581 − 1\| \= 0\.419
\|0\.537 − 0\| \= 0\.537
\|0\.564 − 0\| \= 0\.564
\|0\.590 − 1\| \= 0\.410

MAE \= (0\.419 \+ 0\.537 \+ 0\.564 \+ 0\.410\) / 4 \= 1\.930 / 4 \= 0\.483

**MAE dropped from 0\.490 → 0\.483\.** A small improvement — our nudge helped a little. Factories A and D (true bottlenecks) got higher predictions; B and C also got slightly higher, which hurts. A good optimizer would find the weight that moves A and D up *without* also moving B and C.


LC 03Training logic

Why didn't MAE drop more when we increased w₁? What's the fundamental limitation?


A We didn't increase w₁ enough — a larger change would fix it
B A single weight controls all nodes equally — we can't push A and D up without also pushing B and C up
C MAE is the wrong loss function for this problem


Hint
Reveal Answer

💡 Look at the errors for B and C after the weight nudge. Did they get better or worse? Why might a single shared weight struggle to separate high\-x bottlenecks from high\-x non\-bottlenecks?
**B is correct.** w₁ multiplies every node's feature — so increasing it raises all predictions proportionally. Factory C has x \= 0\.6, which is nearly as high as Factory A (x \= 0\.8\), so it also gets a higher prediction even though it's not a bottleneck. A single\-feature, single\-hidden\-neuron network has very limited expressive power. This is exactly why deeper networks with more neurons — and why GNNs that also use structural information — perform better.


---


Part 2
## Graph Neural Network — *neighbors talk to each other*


 Now we add the graph structure. Before the neural network runs, each node *aggregates messages from its neighbors*. This enriched input — the node's own feature *plus* a summary of its neighbors' features — becomes the input to the neural network. Same weights, new inputs.


Step 6### Aggregate neighbor messages — compute each node's enriched input x̃


Each node's new input is: **its own feature \+ the mean of its neighbors' features**. This is the "mean aggregation" rule, one of the simplest GNN aggregation strategies.


x̃ᵢ \= xᵢ \+ mean(x of neighbors of i)

── Factory A (neighbors: none — A has no in\-neighbors) ──
x̃\_A \= 0\.8 \+ 0 \= 0\.80
(A has no incoming edges in our directed graph)
── Factory B (in\-neighbor: A) ─────────────────────────
x̃\_B \= 0\.3 \+ mean(x\_A) \= 0\.3 \+ 0\.8 \= 1\.10
(B receives a shipment from A)
── Factory C (in\-neighbor: A) ─────────────────────────
x̃\_C \= 0\.6 \+ mean(x\_A) \= 0\.6 \+ 0\.8 \= 1\.40
(C also receives from A)
── Factory D (in\-neighbors: B and C) ──────────────────
x̃\_D \= 0\.9 \+ mean(x\_B, x\_C) \= 0\.9 \+ mean(0\.3, 0\.6\) \= 0\.9 \+ 0\.45 \= 1\.35
(D receives from both B and C)

**Notice:** x̃ values can now exceed 1\.0 — that's fine, the activation function will handle it. More importantly, D now has a different x̃ than B or C, reflecting its position as a convergence point in the supply chain. The *structure* is now part of the input.


LC 04Message passing

Factory D has the highest x̃ \= 1\.35, yet its own feature (x \= 0\.9\) is only slightly higher than A's (x \= 0\.8\). Why did D end up with such a high enriched input?


A Because D has the highest raw output feature
B Because D receives inputs from two neighbors, amplifying the neighborhood signal
C Because the GNN weights are larger for D


Hint
Reveal Answer

💡 Compare x̃\_A and x̃\_D. A also has a high raw feature. What does D have that A doesn't?
**B is correct.** D sits at the convergence of two upstream factories (B and C). Their average feature value (0\.45\) adds on top of D's own value (0\.9\). A, despite high output, has no incoming dependencies — it's the chain's source. The GNN captures this structural difference. The weights are shared across all nodes — C is wrong.


Step 7### Run the same neural network — now on x̃ instead of x


Same weights as Part 1 (w₁ \= 0\.5, w₂ \= 0\.4, b \= 0\.1\). Same formulas. But now x̃ is the input.


── Step 7a: weighted sum z ─────────────────────────────
z\_A \= 0\.5 × 0\.80 \+ 0\.1 \= 0\.40 \+ 0\.10 \= 0\.50
z\_B \= 0\.5 × 1\.10 \+ 0\.1 \= 0\.55 \+ 0\.10 \= 0\.65
z\_C \= 0\.5 × 1\.40 \+ 0\.1 \= 0\.70 \+ 0\.10 \= 0\.80
z\_D \= 0\.5 × 1\.35 \+ 0\.1 \= 0\.68 \+ 0\.10 \= 0\.78
── Step 7b: ReLU (all positive → pass through) ─────────
h\_A \= 0\.50, h\_B \= 0\.65, h\_C \= 0\.80, h\_D \= 0\.78
── Step 7c: output layer ────────────────────────────────
output\_raw\_A \= 0\.4 × 0\.50 \= 0\.200 → ŷ\_A \= σ(0\.200\) \= 0\.550
output\_raw\_B \= 0\.4 × 0\.65 \= 0\.260 → ŷ\_B \= σ(0\.260\) \= 0\.565
output\_raw\_C \= 0\.4 × 0\.80 \= 0\.320 → ŷ\_C \= σ(0\.320\) \= 0\.579
output\_raw\_D \= 0\.4 × 0\.78 \= 0\.312 → ŷ\_D \= σ(0\.312\) \= 0\.577


Step 8### Compute GNN MAE and compare to Part 1


── GNN errors ──────────────────────────────────────────
\|ŷ\_A − y\_A\| \= \|0\.550 − 1\| \= 0\.450
\|ŷ\_B − y\_B\| \= \|0\.565 − 0\| \= 0\.565
\|ŷ\_C − y\_C\| \= \|0\.579 − 0\| \= 0\.579
\|ŷ\_D − y\_D\| \= \|0\.577 − 1\| \= 0\.423

GNN MAE \= (0\.450 \+ 0\.565 \+ 0\.579 \+ 0\.423\) / 4 \= 2\.017 / 4 \= 0\.504

**The GNN MAE (0\.504\) is slightly worse than the plain NN (0\.490\) with these random starter weights.** This is normal and expected — untrained GNNs don't magically outperform plain NNs with the same random weights. The GNN's advantage emerges after training, because it has access to more information (structure \+ features). With random weights, the neighborhood aggregation actually adds noise.


LC 05GNN vs NN

The GNN MAE is slightly worse than the plain NN. Does this mean GNNs are worse models for this problem?


A Yes — if GNN starts worse, it will always perform worse after training
B Yes — GNNs are only useful when the graph has hundreds of nodes
C No — untrained GNNs use random weights on richer inputs; after training, the graph structure provides signal the plain NN can never access


Hint
Reveal Answer

💡 Think about what information is available to each model. The plain NN only sees x. The GNN sees x plus neighborhood structure. After training, which model has more to work with?
**C is correct.** Random weight initialization is a red herring — both models start from roughly random performance. What matters is the information available after training. The GNN can learn that "high\-output nodes that are also downstream convergence points are high\-risk" (Factory D). The plain NN can only learn "high\-output nodes are high\-risk," which incorrectly flags Factory C's neighbor A while missing D's structural role.


---


Summary
## Side\-by\-Side *Comparison*


| Quantity | Plain Neural Network | Graph Neural Network |
| --- | --- | --- |
| **Input to network** | x (own feature only) | x̃ \= own feature \+ mean neighbor feature |
| **Weights used** | w₁\=0\.5, w₂\=0\.4, b\=0\.1 | Same — no extra weights needed for aggregation |
| **ŷ\_A** (true: 1\) | 0\.550 | 0\.550 |
| **ŷ\_B** (true: 0\) | 0\.525 | 0\.565 ↑ |
| **ŷ\_C** (true: 0\) | 0\.540 | 0\.579 ↑ |
| **ŷ\_D** (true: 1\) | 0\.555 | 0\.577 ↑ |
| **MAE (starter weights)** | 0\.490 | 0\.504 (slightly worse) |
| **What it can learn** | Patterns in individual node features | Patterns in features *and* network position |
| **After training: expected advantage** | Cannot detect convergence\-point risk | Can detect that D is a downstream bottleneck |


LC 06Concept transfer

In a real supply chain with 500 factories, which structural pattern would a trained GNN be best at detecting — compared to a plain NN?


A Factories with unusually high output features
B Factories that aggregate inputs from many high\-output suppliers — structural bottlenecks invisible in node features alone
C Factories with the most years of operating data


Hint
Reveal Answer

💡 Think about what extra information x̃ encodes that x doesn't. What structural role did Factory D play that wasn't visible in its raw feature alone?
**B is correct.** A plain NN can detect "this factory has high output" — which is just reading the feature. A GNN can additionally detect "this factory sits at the confluence of many high\-output upstream nodes" — a structural bottleneck whose risk isn't encoded in its own feature. In supply chain risk, these convergence nodes are often the most dangerous single points of failure, and they're exactly what graph structure reveals.


## ✏️ Sketchpad Prompt


Put down the keyboard. On your sketchpad, draw a six\-node supply chain of your own design. Label each node with an x value between 0 and 1\. Choose which nodes are true bottlenecks (label them y \= 1\) and which aren't (y \= 0\).


Now trace one message\-passing step by hand: for each node, write down x̃ \= x \+ mean(neighbors' x). Circle the node where x̃ is highest. Is that node a true bottleneck? Does the GNN have a chance of getting it right with appropriate trained weights? Why or why not?


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · AI \& ML · GNN Forward Pass by Hand**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# GNN + XGBoost · Supplier Disruption Risk · SYSEN 5470

_Source: docs/case-studies/gnn-xgboost.html_

Skip to content


SYSEN 5470 · Network Science · Case Study · Skill: Predict


# Predicting Supplier Disruption with *GNN \+ XGBoost*


Explore how graph neural networks encode network structure as node embeddings, and how those embeddings help XGBoost predict which suppliers will experience disruptions — controlling for position in the supply network.


### Pipeline — Click a Step to Explore


Part 1Network Data
→
Part 3Static GNN
→
Part 3Embeddings → XGBoost
→
Part 4Temporal GNN
→
Part 4Temporal XGBoost


**Part 1 — Network Setup.** This supply chain has **22 supplier nodes** and **38 directed edges** (supplier → buyer). Node size encodes degree. Node color encodes disruption status in the next quarter. Click any supplier to inspect its features.


 The key question: can we predict which suppliers will experience disruptions — and does knowing *where they sit in the network* help?


**Part 3 — Static GNN: Message Passing.** A GraphSAGE model runs **2 rounds of message passing** on this snapshot. In each round, every node asks its neighbors: *"what do your features look like?"* It aggregates those answers (weighted mean) and combines them with its own features to produce an updated representation.


 After 2 rounds, each node's vector encodes not just its own delay rate and size — but a summary of its **2\-hop neighborhood's structure**. That's the embedding. Click nodes to see their embedding visualization.


**Part 3 — Embeddings → XGBoost Feature Table.** The GNN produces one **32\-dimensional embedding vector** per node. These are appended to the node feature table as extra columns. XGBoost then trains on the combined table: raw features *plus* structural features.


 Compare AUC scores: raw features only vs. raw \+ embeddings. The gain tells you how much the network structure added beyond what firms' own attributes already captured.


**Part 4 — Temporal GNN.** Now we have **12 monthly snapshots**. For each snapshot, the GNN produces one embedding matrix. We stack these into a panel dataset: each row is *supplier × month*. We also add a **lagged embedding** (embed at t−1\) as an additional feature — encoding how each supplier's structural position has *changed* over time.


 Use the slider to step through months and watch how node risk profiles shift as the network evolves.


**Part 4 — Temporal XGBoost.** Three models now compete: (1\) raw features only, (2\) raw \+ static embedding, (3\) raw \+ temporal embedding with lag. Each row in the training data is a supplier\-month observation.


 The residual autocorrelation check tells us: after the model's predictions, are the *errors* serially correlated over time? If yes, we're missing a lag structure. The correct answer here: **yes**, there's autocorrelation at lag 1 — meaning disruptions tend to persist into the next month, and adding a disruption\-lag feature would improve the model.


**22** suppliers
**6** disrupted next quarter
 Node size \= degree
Month: **T1**


### Temporal Snapshot


T1

T12
T1

Drag to step through 12 monthly snapshots. Watch how disruption risk migrates through the network as upstream disruptions propagate.


### Model Comparison — AUC\-ROC


### Supplier Info


🏭
 Click any supplier node to inspect its features and embedding.


### Network Metrics


Nodes22
Edges38
Density0\.083
Avg. Degree3\.45
Disruption Rate27%
Avg. Path Length2\.8


### Legend


Disrupted next quarter
Stable next quarter
Critical hub (high degree)
Embedding vector (32\-dim)


 Node size encodes degree centrality. Edge width encodes transaction volume.


### XGBoost Feature Table


Each row \= one supplier. Columns \= raw features \+ GNN embedding dimensions \+ outcome label.

📋 Show / Hide Table


Learning Checks


LC 01 — Direct Observation
Look at the supply network in Part 1 mode. Supplier *Shenzhen\_Fab* has a low historical delay rate (0\.04\) but is marked as disrupted next quarter. Which structural feature best explains why a node with good individual performance still carries high disruption risk?


AShenzhen\_Fab has the highest degree in the network, so it is involved in too many transactions to manage reliably.
BShenzhen\_Fab is downstream from two high\-delay suppliers that are sole\-source dependencies, so upstream risk propagates regardless of its own performance.
CShenzhen\_Fab's delay rate is simply mislabeled — a rate of 0\.04 would prevent any disruption under standard supply chain models.


💡 Hint
🔓 Reveal Answer

Click Shenzhen\_Fab in the network. Then click its upstream neighbors (the nodes with edges pointing toward it). Check their delay rates in the node info panel. What do you notice about their individual risk levels?
**B is correct.** This is the core insight GNNs are built to capture. A node's own features (delay rate \= 0\.04\) look fine in isolation — but the GNN's message passing aggregates information from Shenzhen\_Fab's neighborhood. Both its upstream suppliers have high delay rates and sole\-source flags, meaning there is no backup if either fails. The GNN embedding encodes this neighborhood risk; a flat feature table would miss it entirely. Option A is wrong — high degree helps diversify risk, not concentrate it. Option C reveals a common misconception: individual performance metrics don't account for structural exposure.


LC 02 — Intervention
Switch to *Embeddings → XGBoost* mode and examine the AUC comparison. The model trained on raw features alone achieves AUC \= 0\.71\. After adding GNN embeddings, AUC rises to 0\.84\. What does the SHAP analysis reveal about *why* embeddings help — and what does that tell you about the limits of firm\-level data?


AThe embeddings simply add more features, and more features always improve XGBoost regardless of their content.
BThe top SHAP contributors include several embedding dimensions, indicating that structural position — specifically exposure to upstream risk clusters — carries predictive signal that firm\-level attributes cannot capture.
CThe AUC gain is driven entirely by country risk index, which the GNN encodes more efficiently than the raw feature.


💡 Hint
🔓 Reveal Answer

Navigate to the Embeddings → XGBoost pipeline step. Examine the AUC bars and SHAP breakdown shown there. Which feature block (raw vs. embedding) contributes more to the gain? Consider: if adding random noise columns to XGBoost also "added more features" — would that improve AUC?
**B is correct.** SHAP shows that embedding dimensions rank among the top predictors, alongside financial health score and delay rate. The key interpretation: the embedding dimensions encode neighborhood structure — things like "this node is two hops from a known disruption cluster" or "this node's upstream suppliers are highly interconnected" — which cannot be derived from any single firm's own records. Option A is wrong: adding uninformative features doesn't improve XGBoost — it has regularization to suppress noise. Option C is wrong because country risk appears in the raw features already; the GNN doesn't add new information about it, only about structural position.


LC 03 — Concept Transfer
In the Temporal XGBoost model (Part 4\), adding a *lagged embedding* (the GNN embedding from t−1\) further improves AUC over the static embedding model. A residual autocorrelation check also shows significant autocorrelation at lag 1\. What does this combination of results tell you about the nature of supply chain disruptions?


ADisruptions are essentially random shocks with no memory — the autocorrelation is a statistical artifact of the small dataset and the lagged embedding adds noise.
BDisruptions are persistent and structurally contagious: a supplier at risk in month T is more likely to be disrupted in month T\+1, and the structural exposure encoded in the lagged embedding captures the propagation pathway before the disruption fully materializes.
CThe lagged embedding improves AUC simply because it provides more recent data about firm\-level delay rates, which fluctuate seasonally.


💡 Hint
🔓 Reveal Answer

Use the temporal slider to move through snapshots T6–T9\. Watch which nodes shift from stable to disrupted. Do disruptions appear suddenly and randomly, or do they seem to track along network edges — spreading from disrupted upstream nodes to their downstream neighbors over subsequent months?
**B is correct.** The lag\-1 residual autocorrelation confirms that the model at time T is systematically under\-predicting disruptions that persist from T−1\. This means disruptions have memory — a disrupted supplier stays disrupted, and its downstream partners become increasingly exposed over subsequent periods. The lagged embedding captures the *structural pathway* of that exposure: as upstream nodes enter distress, the neighborhood structure changes in ways the GNN can encode, providing an early warning signal before the downstream disruption shows up in firm\-level metrics.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · GNN \+ XGBoost · Supplier Disruption Risk**

 Cornell Engineering · Summer 2026 · ← All case studies

---

# Network Joins · SYSEN 5470

_Source: docs/case-studies/joins.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Identify


# Network Joins: Getting *Node Attributes* onto Edges


You have factory metadata in one table and shipments in another — but to answer questions like *"how much volume flows from Tier 3 to Tier 1?"* you need them joined together. Build the join, the rename, the grouping, and the summary step by step using the drag\-and\-drop code builder in either R or Python. The result table and flowchart update live. Use it as your calculator for the learning checks.


⚠ Synthetic supply\-chain data — illustrative, not from any real company


Language:

R · dplyr
Python · pandas


Both produce the same answers. Builder, hints, code, and flowchart all switch with this toggle. Your pipeline is preserved when you switch.


### 📦 The two source tables — your raw data


#### nodes — one row per factory nodesnodes\_df


Each factory has a region, tier, and capacity. Tier 1 \= final assembly, Tier 2 \= subassembly, Tier 3 \= raw component.


#### edges — one row per shipment lane edgesedges\_df


Each row is a regular shipment lane between two factories during Q1\. `from_id` and `to_id` reference the `node_id` in the nodes table.


**Note the asymmetry:** edges have `from_id` and `to_id`, but the node table calls the same field `node_id`. That mismatch is the first thing every real network join has to solve, in either language.


### ✏️Sketchpad Moment (do this before touching the builder)


On your physical sketchpad:


1. Sketch the two tables side by side. List the column names of each.
2. **Draw an arrow** from `edges.from_id` to `nodes.node_id`. This arrow is your join key — the visual definition of a join. It exists independently of whether you'll write the code in R or Python.
3. Now sketch what the joined table would look like. Which columns survive? How many rows? What happens to `tier` if you join twice — once on `from_id` and once on `to_id`? Draw what you think the column names will look like.
4. Question to write down: when does the rename step become essential, and what columns is it renaming?


Then come back here, pick your language, and verify your sketch with the builder. Sketches first, syntax second.


### 🛠 Code builder — drag chips into the pipeline; drag placed chips to reorderR · dplyr


WORD BANK · drag (or double\-click) any chip into the pipeline


YOUR PIPELINE · drag chips to reorder · click ✕ to remove


Drag chips here to build a pipeline. Start with a table.


▶ Run pipeline
Clear
Load example


Generated code
R
📋 Copy code

Build a pipeline to see the equivalent code here.


No pipeline run yet. Drag chips, then click "Run pipeline".


### 📊 Process flowchart — live diagram of your pipeline


Each chip in your pipeline becomes a node here. Shapes and colors classify the operation: 📦 tables, 🔧 joins, 🏷 renames, 🔍 filters, 📑 groups, Σ summaries.


↓ Vertical
→ Horizontal

📋 Copy Mermaid code
📋 Copy SVG


Build a pipeline to see the flowchart here.


LC 01
Build a pipeline that joins the `edges` table to the `nodes` table to get the **origin factory's tier** onto each shipment, then **rename the joined columns** with an `_origin` suffix so they're easy to reference. Then count how many shipment rows originate from **Tier 3** factories. (You'll find that without the rename step, your filter chips won't have a column to reference!)


YOUR ANSWER:


💡 Hint
🔓 Reveal Answer


LC 02
Now answer the real engineering question: **what is the total shipment volume (sum of `volume_units`) flowing from Tier 3 suppliers to Tier 1 assemblers?** You'll need to join twice (once for origin, once for destination) and rename twice (once with `_origin`, once with `_dest`) — the second join is where the name collision really bites if you skip the rename.


YOUR ANSWER:


💡 Hint
🔓 Reveal Answer


LC 03


A
B
C


💡 Hint
🔓 Reveal Answer


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Big Network Data · Joins Builder Lab**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Network Permutation Testing · SYSEN 5470

_Source: docs/case-studies/permutation.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Infer


# Does Income Shape Who Rides With Whom?*Permutation Testing* a Mobility Network


Boston's Bluebikes program connects neighborhoods — but does ridership flow freely across income lines, or do high\-income neighborhoods mostly exchange riders with each other? Use permutation testing to find out whether the observed income pattern could arise by chance.


### 📍 Boston Bluebikes — AM Rush Hour Ridership Network


👁 Observed
⟳ Unblocked Permutation
⟳ Block Permutation
⊞ Compare All Three


 High\-income neighborhood
 Low\-income neighborhood
 Block A (high\-traffic)
 Block B (low\-traffic)

Node size \= total ridership. Arrow thickness \= ride count. **Click a node** to inspect.


#### ● Observed


—


#### ⟳ Unblocked Perm


—


#### ⟳ Block Perm


—


 High\-income
 Low\-income
 Block A
 Block B


 Notice: **block\-permuted** networks keep thick edges thick — they preserve traffic\-tier structure. **Unblocked** permutations can place any weight anywhere.


### 🔀 Run Permutations


⟳ \+1 Unblocked
⟳ \+1 Blocked
\+25 Unblocked
\+25 Blocked
\+200 Both
↺ Reset


 Unblocked: 0  \|  Blocked: 0


**Why does block permutation matter?** In Boston's hub\-and\-spoke bike network, Block A edges carry high\-volume AM commuter flows shaped by station capacity and geography — constraints Block B recreational edges don't share. A naive unblocked permutation can put a 280\-ride commuter weight onto a casual weekend route, generating null networks that are physically impossible. **Block permutation** shuffles only within traffic tiers, so every null network remains realistic.


### 📊 Ridership Share by Income\-Pair Type


 Dashed line \= 25% (expected under equal mixing). **Similarity Index**: 0 \= perfectly heterogeneous; 1 \= fully within\-group concentration.


### 📐 Similarity Index


Current network
—
Click "Observed" to begin

Observed value—
Median (unblocked)—
Median (blocked)—
p\-value (unblocked)—
p\-value (blocked)—
p\-value \= share of permuted networks with index ≥ observed (one\-tailed).


### 🏙 Node Inspector


🖱️ Click any neighborhood to inspect


Income Tier


Total Rides


Out\-routes


In\-routes


### 📈 Null Distribution


Histogram of permuted similarity indices. Dashed amber line \= observed. Keep permuting to build the distribution.


### ✏️ Sketchpad Prompt


**Before you permute:** On your sketchpad, draw the 5 neighborhoods as labeled circles. Mark each as high\-income (amber) or low\-income (indigo) — then sketch where you expect most arrows to point and which pairs you think carry the heaviest ridership. After running 50\+ permutations of each type, draw two rough null distributions from memory. Where does the observed value sit relative to each? Does income structure appear to shape ridership beyond what chance would produce?


Learning Checks


LC 01
In the observed network, which income\-pair type accounts for the largest share of AM rush\-hour ridership?

ALow\-income → Low\-income
BHigh\-income → High\-income
CLow\-income → High\-income


💡 Hint
🔓 Answer

Click "👁 Observed" first, then read the bar chart. Node color (amber \= high\-income, indigo \= low\-income) shows you which neighborhoods are which.
**B — High\-income → High\-income.** Back Bay and Downtown Crossing are both high\-income, and the heavy commuter corridor between them dominates ridership volume. This pattern is what we want to test: is it statistically unusual, or could it arise simply from random reshuffling of the same weights?


LC 02
Switch to "Compare All Three" and run a few permutations. In the block\-permuted network, thick edges stay thick. Why does this matter for the validity of the test?

AIt doesn't matter — any permutation is valid as long as total edge weight is preserved.
BHigh\-traffic edges reflect structural constraints (hub\-and\-spoke routing), so swapping their weights with low\-traffic edges creates null networks that couldn't actually occur.
CBlock permutation is always more conservative, so it always produces a higher p\-value.


💡 Hint
🔓 Answer

Think about what an unblocked permutation could do: it might place a 280\-ride weight on an edge that only ever sees 120 rides. Is that physically plausible in a system with fixed station locations and docking capacity?
**B — Block permutation preserves structural realism.** In Boston's hub\-and\-spoke system, Block A edges carry commuter flows constrained by station geography and capacity — constraints Block B recreational edges don't share. Swapping a 280\-ride commuter corridor weight onto a casual route creates an impossible null network. Unblocked permutations do this freely, making them anti\-conservative for hub\-and\-spoke systems. Option C is wrong: which test is more conservative depends on where the observed value falls relative to each null distribution — it's not a universal rule.


LC 03
After 200\+ permutations each, the unblocked test gives a lower p\-value than the blocked test. A planner concludes the unblocked result is "stronger evidence" of income homophily. What's the flaw?

ANothing — a lower p\-value always means stronger evidence.
BThe unblocked null distribution is more spread out than physically realistic, making the observed value appear rarer than it actually is.
CThe planner should choose whichever test supports their policy argument.


💡 Hint
🔓 Answer

Look at the null distribution. Are the unblocked and blocked histograms centered in the same place? If the unblocked null is shifted lower, what does that mean for how "extreme" the observed value looks by comparison?
**B — The unblocked null is artificially spread, inflating significance.** Because unblocked permutations scatter any weight onto any edge (including placing commuter\-volume weights on recreational routes), they generate null networks more heterogeneous than anything that could actually exist. This pulls the null median lower and widens variance, making the observed index look more extreme — and producing an artificially small p\-value. The "stronger evidence" is an artifact of an unrealistic null, not a genuine signal. The blocked test, whose null networks all obey the system's structural constraints, is the more defensible choice — even if the p\-value is less dramatic.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Permutation Testing on Mobility Networks**

 Cornell Engineering · Summer 2026 · ← All case studies

---

# Sampling Big Networks · SYSEN 5470

_Source: docs/case-studies/sampling.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Identify


# Sampling Big Networks: *What Survives the Cut*


You are an analyst studying evacuation flows during a Gulf hurricane. The full network has 40 parishes and hundreds of weighted flow edges — too big to wrangle on your laptop. Pick a sampling strategy, choose a sample size, and watch which features of the network survive. Some strategies preserve geographic coverage. Some preserve triangles. None preserve everything.


## 📍 Coastal Louisiana Evacuation Network


RANDOM NODE · 25%


 **10**/40 nodes sampled
 **30** not in sample
📐 **0** edges retained


 🎲 Random Node
 UNIFORM NODE DRAW · INDUCED EDGES


 👁 Ego\-Centric (1\-hop)
 SEED \+ IMMEDIATE NEIGHBORS


 ❄ Snowball (2\-hop)
 SEED \+ 2 WAVES OUT


 🔗 Random Edge
 EDGE DRAW · KEEP ENDPOINTS


Sample size

25%


🎲 Resample
👁 Show Full Network


### 📊 Sample vs. Population


Node coverage—
Edge coverage—
△ Triangles—
Triangle preservation—

Mean degree (sample)
—
true: —


### 🌎 Geographic Coverage


URBAN CORE
SUBURBAN
COASTAL
CORRIDOR
INLAND
EAST BANK


### 🎨 Legend


Sampled node (in your data)
Seed node (ego/snowball only)
Outside your sample
Triangle\-forming edge


### ✏️ Sketchpad Moment — Before You Click


Open your sketchpad. Without running the visualization, draw a quick map: **which 5 of these 40 parishes would you measure** if you could only afford 5? Mark them. **Then write down what you expect to lose** — geographic blind spots, missing triangles, biased degree estimates. Now resample with each strategy at 12\.5% (5 nodes worth) and see whether the strategies even produce the kind of network you expected.


### 🧭 Why this matters for an engineer


You will rarely be handed the full network you care about. Sensor budgets, API rate limits, IRB constraints, or sheer N² scaling will force you to sample. The decision is not *whether* to sample but **which features you are willing to lose**. A supply\-chain analyst studying disruption cascades needs triangles preserved. A logistics planner needs geographic coverage. A surveyor estimating average ties per actor needs unbiased degree. Each strategy below is optimal for a different question — and disastrous for the others.


**The four strategies in this lab**: (1\) *Random node* — pick nodes uniformly, keep only edges between sampled nodes. (2\) *Ego\-centric* — pick seed nodes, snowball one step out to all neighbors. (3\) *Snowball\-2* — extend that two hops. (4\) *Random edge* — pick edges uniformly, keep their endpoints. Resample multiple times under each strategy to see how much sampling variability matters.


### 📝 Learning Checks


LC 01
Set the sample size to **30%**. Cycle through all four strategies (resample a few times each). Which strategy reliably captures the most *nodes* in your final sample?


ARandom node — because you're directly drawing 30% of nodes
BSnowball\-2 — because each seed pulls in neighbors and their neighbors
CRandom edge — because you usually pick more than 30% of edges


💡 Hint
🔓 Reveal Answer


**Hint:** Watch the "Node coverage" metric in the top right as you cycle strategies at the same 30% setting. The 30% slider means different things under different strategies — for ego/snowball, it controls how many *seeds* you draw, not how many total nodes end up in the sample.


**Answer: B.** Snowball\-2 typically pushes node coverage past 80% even when only 30% of nodes are seeds, because the second hop pulls in friends\-of\-friends across the entire connected component. Ego\-centric is similar but smaller. Random node is exactly the slider value (\~30%) because there is no neighborhood expansion. Random edge varies — it tends to recruit \~40–55% of nodes since each edge brings in two endpoints, but with replacement collisions. The trap in this question: A is "right" in a literal accounting sense but loses to B in actual coverage.


LC 02
Set the strategy to **Random Edge** at **30%**. Resample five times. Compare the *Triangle preservation* and *Mean degree* metrics to the values you get from **Random Node** at the same 30%. What pattern do you observe?


ARandom edge preserves triangles better, because more edges \= more triangles
BRandom edge destroys triangles disproportionately, because closing a triangle requires keeping all three of its edges — a small chance under independent edge sampling
CBoth strategies preserve triangles equally well at 30%


💡 Hint
🔓 Reveal Answer


**Hint:** Think probabilistically. If you sample each edge independently with probability p, what's the probability that all three edges of a specific triangle survive? Compare that to keeping a triangle under random *node* sampling, where keeping the three nodes suffices.


**Answer: B.** Under independent edge sampling at rate p, a triangle survives only if all three of its edges are kept — probability p³. At p \= 0\.30 that's just 2\.7%. Under random node sampling at rate p, a triangle survives if all three nodes are kept — probability p³ as well (still 2\.7%), *but the induced edges are automatically retained*, so triangle preservation aligns with node\-triple preservation. In practice random edge sampling shows much more variance in triangle counts because triangles share edges, breaking independence. This is one of the canonical reasons sociologists prefer node\-based designs when clustering is the quantity of interest.


LC 03
Run **Ego\-Centric** sampling several times at 15% seeds. Notice the "Mean degree (sample)" metric versus the "true" mean degree shown below it. Why does ego\-centric sampling produce a *biased* estimate of mean degree even when it captures most of the network?


ABecause the seeds were drawn randomly, the sample is unbiased — any discrepancy is just sampling variation
BHigh\-degree nodes are more likely to be a neighbor of *some* seed (because they have many neighbors), so they enter the sample at a higher rate than their share of the population — the friendship paradox baked into the design
CEgo\-centric sampling under\-counts edges between non\-seed nodes, which deflates degree


💡 Hint
🔓 Reveal Answer


**Hint:** Think about who is *more likely* to be a neighbor of a randomly picked seed. If you pick one random person and look at their friends, are those friends a random sample of the population — or are they systematically the kinds of people who have many friends?


**Answer: B.** This is the *friendship paradox* embedded in ego\-centric sampling. A node with degree d gets sampled (as a neighbor of a seed) with probability proportional to d — so high\-degree nodes are over\-represented relative to their population share. The mean degree in your sample is thus inflated. C is partially true but secondary; the dominant effect is the inclusion bias. This is why epidemiologists and survey methodologists distinguish "ego\-centric" from "respondent\-driven" designs with weighting corrections — and why naive snowball samples systematically overestimate degree, density, and clustering.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Big Network Data · Sampling Strategies Lab**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Supply Chain Resilience · SYSEN 5470

_Source: docs/case-studies/supply-chain.html_

Skip to content


SYSEN 5470 · Network Science · Interactive Lab · Skill: Measure


# Supply Chain Networks \& *Flow Resilience*


Explore how goods flow from raw\-material suppliers to end customers — and discover why the busiest node in a supply chain is rarely the most critical one to protect.


 **—** active nodes
 **0** disrupted


### 🔍 Node Inspector


🖱️Click any node to inspect its supply chain role.


✂️ Disrupt Node
↩ Restore
⚡ 50% Capacity
✕ Deselect


### 📊 Network Metrics


🏪 Retailers Supplied—
📦 Supply Coverage—
📏 Avg Path Length—
🔗 Components—
↔️ Diameter—
⚡ Capacity shock active: **—** at 50% output


### 🎮 Controls


Click a node on the map to select it, then use the buttons above.


🔄 Reset All


### 🗺️ Legend


Raw material supplier (upstream)
Hub / consolidator (midstream)
Distribution center
Retailer / end customer

High\-volume corridor
Standard route
Node size \= weighted degree


### 📋 Data Tables


Nodes
Edges


| Node | Zone | Role | Degree | Betweenness | Status |
| --- | --- | --- | --- | --- | --- |


| From | To | Type | Vol (units/wk) |
| --- | --- | --- | --- |


Learning Checks


LC 01
Which single node disruption causes the greatest loss of retailer coverage — and is it the node with the most connections?

AYes — the Central Hub has the most connections and removing it causes the most retailers to lose supply.
BNo — the Mesa Consolidator has fewer connections but removing it isolates more retailers than removing the Central Hub.
CThe highest\-degree node is always most critical, because more connections means more downstream dependency.


💡 Hint
🔓 Reveal Answer

Try removing the **Central Hub** and record "Retailers Supplied." Then hit Reset, remove **Mesa Consolidator**, and compare. Which loss is worse?
**Correct: B.** Removing Mesa Consolidator strands the entire Southwest retail cluster — a larger coverage loss than removing the Central Hub, which serves regions with redundant paths from other DCs. This is the core gap between *degree* and *betweenness*: what matters isn't how many routes touch a node, but whether those routes are the *only* paths to critical customers. High\-degree nodes are often visible enough that engineers build redundancy around them. The quiet bottlenecks — low\-degree, high\-betweenness — are where supply chains actually break.


LC 02
Remove the Mesa Consolidator. What happens to the network's component structure — and which retailers are now completely cut off from supply?

AThe network stays connected. All retailers still receive supply through alternative routes, just with longer delivery paths.
BThe network splits into disconnected components. The Southwest retail cluster loses all supply and average path length becomes infinite.
CThe network splits, but the Central Hub immediately compensates so the Southwest cluster stays partially supplied.


💡 Hint
🔓 Reveal Answer

Select **Mesa Consolidator** and click "Disrupt Node." Watch the **Components** and **Avg Path Length** metrics change. Then look at which nodes have gone dark on the map.
**Correct: B.** Mesa Consolidator is a *bridge node* — the sole connector between the Southwest supplier cluster and its retail cluster. Removing it creates two disconnected subgraphs, and average path length becomes ∞ because no finite path exists between those components. Networks don't need to lose many nodes to fragment — they only need to lose the *right* one. This is why bridge detection is a core task in supply chain resilience analysis, and why betweenness centrality is a better vulnerability signal than degree.


LC 03
Select the Northern Raw Supplier and apply a 50% capacity shock (⚡ button). Does cutting its output by half cut total retailer coverage by roughly half?

AYes — a 50% reduction in supplier output causes roughly 50% of retailers to lose supply, since they depend on that source.
BYes — coverage loss is actually worse than 50%, because downstream nodes have no way to compensate for upstream shortfalls.
CNo — retailer coverage stays the same (all retailers still reachable), because path connectivity is unaffected. Only throughput volume drops, not reachability.


💡 Hint
🔓 Reveal Answer

Select **Northern Raw Supplier** and click "⚡ 50% Capacity." Now check: does the **Retailers Supplied** metric change? Compare that to what happens when you fully disrupt the same node. What's the difference between making a link thinner vs. cutting it entirely?
**Correct: C.** A capacity shock reduces the *volume* flowing along a node's edges, but as long as the node remains active, all downstream paths stay topologically connected. Every retailer that was reachable before is still reachable — they'll receive less product, but won't be cut off. This distinction is fundamental in supply chain risk: **connectivity disruptions** (node removal) and **capacity disruptions** (output reduction) have different structural effects and require different interventions. A fully connected but chronically undersupplied network is a different problem from a fragmented one — and fixing it requires a different playbook.


LC 04
Compare disrupting the highest\-betweenness node vs. a peripheral node like Eastern Raw Supplier. Which is worse for *global* network metrics — and which can be uniquely catastrophic for a *specific* retailer cluster?

ARemoving the highest\-betweenness node is always worse by every metric — both globally and for every specific cluster — because betweenness directly measures total criticality.
BRemoving the highest\-betweenness node damages global metrics most, but a peripheral node that exclusively serves one cluster can be just as catastrophic for that cluster even when global metrics look fine.
CRemoving a peripheral node is always less damaging, because low betweenness means the rest of the network is unaffected.


💡 Hint
🔓 Reveal Answer

Remove **Mesa Consolidator** (highest betweenness) and note the global metrics. Reset, then remove **Eastern Raw Supplier**. Global metrics may look healthier the second time — but look specifically at which retailer nodes go dark. Is "the rest of the network is fine" the same as "all customers are fine"?
**Correct: B.** This is the gap between *global resilience* and *local service coverage*. Removing a high\-betweenness node maximizes damage to network\-wide metrics. But removing a peripheral node that is the *sole upstream source* for a specific retail cluster can be equally catastrophic for that cluster — even while the rest of the network runs normally. A supply chain risk manager who only tracks aggregate metrics will miss this. Real resilience analysis requires both: network\-level topology metrics *and* customer\-level coverage audits. Neither is sufficient alone.


**Try this on your own data.** Open the Coding Playground, upload your network, and use the same tools.
→ R Playground
→ Python Playground


**SYSEN 5470 · Supply Chain Networks \& Flow Resilience**

 Cornell Engineering · Summer 2026 · ← All case studies

---

# Network Visualizer · SYSEN 5470

_Source: docs/visualizer.html_

Skip to content


SYSEN 5470 · Tools


# Network *Visualizer*


Bring your own data. Drop an edgelist CSV (and an optional nodelist), pick which columns are **from**, **to**, **weight**, and **time**, and explore. Everything runs locally in your browser — your data never leaves this page.


### 📥 Data


Edgelist CSV required


Nodelist CSV optional


Drop a CSV, or load the sample graph to start.

⟳ Load
▶ Sample


### 🗂 Column Mapping


Upload an edgelist to map columns.


### ⚙ Layout


Force
Radial
Circle
Hier.


### 🎚 Tunables


Node size scale1\.0x


Edge weight threshold0\.0


Time filter (≤)—


### 👁 Display


Node labels
Edge weight labels
Community color
Live drift


### 📤 Export


⤓ Export PNG


Your Network


0Nodes
0Edges shown
0Components
—Density


**No network loaded**
 Upload an edgelist or hit ▶ Sample to start.


### 📖 Quickstart


1. Drop an edgelist CSV. Expected columns: `from, to, weight, time` (any names — you'll map them).
2. Auto\-detection guesses the four columns. Adjust the dropdowns if needed.
3. Click **Load**. The graph renders with force layout; node size encodes degree.
4. Switch layouts, toggle community color, slide the time filter, and export PNG.


### 🏷 Selected Node


Click any node to inspect.


### 📊 Top Degree


Load a network to see rankings.


### 🔗 Top Betweenness


Computed when graph loads (≤600 nodes).


**SYSEN 5470 · Network Visualizer**

 Cornell Engineering · Summer 2026 · All processing happens in your browser.

---

# Coding Playground · SYSEN 5470

_Source: docs/playground.html_

Skip to content


SYSEN 5470 · Coding Playground


# Run Real Code.In the Browser.


No install. No login. No server. The playground runs a full R or Python interpreter inside the browser tab via WebAssembly — and saves your code to your own browser so it's still there when you come back tomorrow. Pick a language to start.


Pick a Language


📊
## R PlaygroundPowered by WebR


A full R interpreter, compiled to WebAssembly. Tidyverse\-flavored, network\-science\-ready.


**Pre\-installed:** dplyr · tidyr · ggplot2 · readr · igraph · tidygraph · DBI · RSQLite


Open R Playground →


🐍
## Python PlaygroundPowered by Pyodide


CPython compiled to WebAssembly. Scientific Python's core packages, ready to go.


**Pre\-installed:** numpy · pandas · networkx · matplotlib · scipy · scikit\-learn


Open Python Playground →


Why two playgrounds?

Each language ships its own \~30MB WebAssembly bundle on first visit (then it's cached). Loading both at once would double the wait. So we keep them on separate pages: pick the one you need, and stick with it for your session. **Your code is auto\-saved to your own browser** (`localStorage`), so it's still there when you come back. **Any CSV files you upload are saved to your browser too** (`IndexedDB`), so they survive a refresh — but they live on your device, never on our server.


Be aware of the limits


⏳
#### First load


\~30MB download the first time you open a playground. After that the browser caches it. Bring patience to the first visit; subsequent visits start in a second or two.


💾
#### Memory ceiling


Browser tabs cap at \~2–4 GB. Plenty for any course dataset but **not** enough to load a million\-row CSV at full resolution. Pre\-aggregate or sample first.


📦
#### Curated packages


Only packages compiled for WebAssembly work. The pre\-installed lists above cover the course. Things needing system libraries (e.g. PyTorch, TensorFlow, heavy GIS stacks) won't install.


🔌
#### Limited networking


HTTP fetches work (CORS permitting); raw sockets and remote\-database connections don't. Load files from URLs or upload them directly.


💡
#### Built for labs, not training jobs


Great for wrangling, visualization, stats, and graph algorithms on small\-to\-medium networks. For training large neural networks, use a real laptop or Posit Cloud.


🔒
#### Private to you


Everything runs in your browser tab. We never see your code or your data. Same goes for the files you upload — they go straight to your browser's local storage.


**SYSEN 5470 · Coding Playground**

 Cornell Engineering · Summer 2026 · WebR \+ Pyodide · 100% client\-side · tmf77@cornell.edu

---

# R Playground · SYSEN 5470

_Source: docs/playground-r.html_

Skip to content


SYSEN 5470 · Coding Playground


# *R* Playground


A full R interpreter, compiled to WebAssembly, running in your browser tab. No install. Tidyverse \+ igraph \+ tidygraph \+ DBI/RSQLite are pre\-installed. Your code and uploaded CSVs are saved to your own browser — they survive a refresh but never leave your device.


Loading WebR runtime…


How this works

* The R interpreter runs **entirely in this browser tab** via WebAssembly. Nothing is sent to a server.
* First load downloads \~30MB of R \+ WASM. Your browser caches it, so subsequent visits start in a second or two.
* A browser tab has a **\~2–4 GB memory ceiling**. Fine for any course dataset; not enough for million\-row CSVs at full resolution.
* Your code is auto\-saved to your browser's `localStorage`. Uploaded files are saved to your browser's `IndexedDB`. Both stay on your device.
* Click **Run** (or press `Ctrl/Cmd + Enter`) to execute the editor's contents. Stdout, plots, and the current workspace populate on the right.


Pre\-installed packages

The packages below are loaded into your session once WebR is ready. To install additional ones, run `webr::install("<pkg>")` if it's available in the WebR CRAN repo.


dplyr
tidyr
ggplot2
readr
igraph
tidygraph
DBI
RSQLite


### 📝 Code Editor


▶ Run
↻ Reset


▾ Load sample…
Karate club (34 nodes)
Lakeside Bikeshare (15 nodes)
Riverdale Metro (18 nodes)
Supply Chain (16 factories)


⬆ Upload CSV


### 📤 Output


Console
Plots 0
Objects 0
Data 0


WebR is loading. The console will activate once the runtime is ready.


No plots yet. Call `plot()`, `ggplot()`, or any graphics function in the editor.


No objects in your workspace yet.


No files uploaded yet. Use ⬆ Upload CSV or ▾ Load sample to bring data into your session.


**Code** auto\-saved to localStorage
**Uploaded files** persisted in IndexedDB (survive refresh, stay on your device)
Clear saved code
Clear uploaded files


**SYSEN 5470 · R Playground** · Powered by WebR · 100% client\-side · tmf77@cornell.edu

---

# Python Playground · SYSEN 5470

_Source: docs/playground-py.html_

Skip to content


SYSEN 5470 · Coding Playground


# *Python* Playground


CPython, compiled to WebAssembly, running in your browser tab. No install. NumPy, pandas, networkx, matplotlib, SciPy, and scikit\-learn are pre\-installed. Your code and uploaded CSVs are saved to your own browser — they survive a refresh but never leave your device.


Loading Pyodide runtime…


How this works

* CPython runs **entirely in this browser tab** via WebAssembly. Nothing is sent to a server.
* First load downloads \~30MB of Python \+ WASM. Your browser caches it, so subsequent visits start in a second or two.
* A browser tab has a **\~2–4 GB memory ceiling**. Fine for any course dataset; not enough for million\-row CSVs at full resolution.
* Your code is auto\-saved to your browser's `localStorage`. Uploaded files are saved to your browser's `IndexedDB`. Both stay on your device.
* Click **Run** (or press `Ctrl/Cmd + Enter`) to execute the editor's contents. **Use `plt.show()`** to send a matplotlib figure to the Plots tab.


Pre\-installed packages

The packages below are loaded once Pyodide is ready. To add more, run `import micropip; await micropip.install("<pkg>")` if it's a pure\-Python wheel or one of Pyodide's curated WASM builds.


numpy
pandas
networkx
matplotlib
scipy
scikit\-learn


### 📝 Code Editor


▶ Run
↻ Reset


▾ Load sample…
Karate club (34 nodes)
Lakeside Bikeshare (15 nodes)
Riverdale Metro (18 nodes)
Supply Chain (16 factories)


⬆ Upload CSV


### 📤 Output


Console
Plots 0
Objects 0
Data 0


Pyodide is loading. The console will activate once the runtime is ready.


No plots yet. Call `plt.show()` in your code to send a figure here.


No objects in your workspace yet.


No files uploaded yet. Use ⬆ Upload CSV or ▾ Load sample to bring data into your session.


**Code** auto\-saved to localStorage
**Uploaded files** persisted in IndexedDB (survive refresh, stay on your device)
Clear saved code
Clear uploaded files


**SYSEN 5470 · Python Playground** · Powered by Pyodide · 100% client\-side · tmf77@cornell.edu

---

# Readings · SYSEN 5470

_Source: docs/readings.html_

Skip to content


SYSEN 5470 · Readings


# Readings


Every case study pairs a textbook chapter with one engineering application paper — the textbook keeps it rigorous, the paper keeps it real. Most links are free or open\-access; excerpts from non\-open texts are distributed as PDFs in the course.


Anchor Texts
Core Textbooks


### 📘 Barabási (2016\) · Network Science


Main textbook. Free online, chapter\-by\-chapter. Cited in every unit.


networksciencebook.com →


### 📗 Easley \& Kleinberg (2010\) · Networks, Crowds, \& Markets


Cornell\-grown. Free PDF. Ties, betweenness, cascades, matching markets.


PDF →


Reference / Extra


### 📙 Menczer et al. (2020\)


A First Course in Network Science. A different voice on the same ideas.


Site →


### 📕 Bertsekas · Network Optimization


Reference for the routing \& optimization unit.


PDF →


By Case Study
## 🕸️Network Fundamentals Identify\#


Classify nodes, edges, direction, weighting, and small\-world phenomena. Recognize when your problem is a graph problem.


Primary
Barabási, Ch. 1: *Introduction*. Why network thinking matters.
Read →


Primary
Barabási, Ch. 2: *Graph Theory*. Nodes, edges, direction, weighting, paths.
Read →


Applied
Gladwell, M. (1999\). *Six Degrees of Lois Weinberg.* The New Yorker.
Open →


Primary
Easley \& Kleinberg, Ch. 3: *Strong and Weak Ties.*
Read →


Optional
Easley \& Kleinberg, Ch. 2: *Graphs*. Great visuals if you want a second pass.
Read →


Lab
Companion lab: *Build a Network.* Construct networks from prose; switch directed/undirected, partition, layout, and watch canvas \+ tables \+ adjacency matrix stay in sync.
Open lab →


## 📊Centrality \& Criticality Measure\#


Identify bottlenecks, hubs, and vulnerabilities in any system. Calculate centrality with tidygraph; bipartite networks; cascading failure.


Primary
Barabási, Ch. 3: *Random Networks.*
Read →


Primary
Barabási, Ch. 8: *Network Robustness.*
Read →


Primary
Barabási, Ch. 10: *Spreading Phenomena.*
Read →


Applied
Easley \& Kleinberg, §3\.6: *Betweenness Measures and Graph Partitioning.*
Read →


Applied
Easley \& Kleinberg, Ch. 19: *Cascading Behavior in Networks.*
Read →


Optional
Easley \& Kleinberg, Ch. 14: *Link Analysis and Web Search.*
Read →


Lab
Companion lab: *Betweenness vs. Degree · Riverdale Metro.*
Open lab →


## 📐Network Statistics — Bluebikes Infer\#


Permutation tests, jackknife, bootstrap on networks. Does income shape who rides with whom?


Applied
Farine, D. R. (2017\). *A guide to null models for animal social network analysis.* Methods Ecol. Evol. 8: 1309–1320\.
DOI →


Lab
Companion lab: *Permutation Testing a Mobility Network.*
Open lab →


## 🚦Routing \& Optimization Predict\#


Solve real flow and routing problems in logistics and transit. Counterfactual graph mutation — add a node, measure metric M, resample.


Primary
Bertsekas. *Network Optimization.* MIT.
PDF →


Applied
*Supply Chain Network Design.* Resource on production\-distribution graph design.
Open →


Lab
Companion lab: *Counterfactual Monte Carlo · Lakeside Bikeshare.*
Open lab →


## 🧩Clustering \& Communities Measure\#


Detect structure in large\-scale networks automatically. Bipartite graphs, affiliation, matching markets.


Primary
Barabási, Ch. 9: *Communities.*
Read →


Applied
Barabási, Ch. 2: §*Bipartite Graphs.*
Read →


Applied
Easley \& Kleinberg, Ch. 10: *Matching Markets* (bipartite focus).
Read →


Applied
Easley \& Kleinberg, §4\.3: *Affiliation.*
Read →


Lab
Companion lab: *DSM Clustering · Rocket / Drone / Software.*
Open lab →


## 🤖AI \& Machine Learning — Supplier Disruption Predict\#


Neural networks, graph neural nets, and ML for network inference. Static and temporal GNNs.


Applied
Khan et al. (2025\). *Optimizing machine learning for network inference.* Sci Rep 15, 24472\.
DOI →


Applied
Resce et al. (2022\). *Machine learning prediction of academic collaboration networks.* Sci Rep 12, 21993\.
DOI →


Optional
Ding (2025\). *A Comprehensive Survey on AI for Complex Networks.* arXiv.
DOI →


Lab
Companion lab: *GNN \+ XGBoost · Supplier Disruption Risk.*
Open lab →


Lab
Companion lab: *GNN Forward Pass by Hand.* Hand\-arithmetic walkthrough of plain NN vs. GNN on a 4\-node graph.
Open lab →


## 🗺️Visualization — Mobility \& Evacuation Identify\#


Communicate network insight with beautiful, interactive graphics. Bluebikes, hurricane evacuation, healthcare accessibility.


Applied
Bellantuono et al. (2025\). *Analyzing the accessibility of Rome's healthcare services via public transportation.* Sci Rep 15, 22880\.
DOI →


Lab
Companion lab: *Network Aggregation for Visualization.* Bluebikes morning flows at three zoom levels — stations, neighborhoods, income quintiles.
Open lab →


## 🗄️Big Network Data Identify\#


Wrangling edgelists and nodelists at scale. Grouping, joins, network joins, aggregation, intro to SQLite.


Primary
Easley \& Kleinberg, §2\.4: *Network Datasets — An Overview.*
Read →


Lab
Companion lab: *Sampling Big Networks.* 40\-parish Gulf evacuation network, four sampling strategies, watch what survives the cut.
Open lab →


Lab
Companion lab: *Network Joins.* Drag\-and\-drop pipeline builder in R (dplyr) or Python (pandas). Join, rename, group, summarise — and see why renames matter on the second join.
Open lab →


**SYSEN 5470 · Readings Library**

 Cornell Engineering · Summer 2026 · Most links are free\-to\-read or open\-access. Excerpts from non\-open texts will be distributed in the course as PDFs.

---

# Sketchpad Prompts · SYSEN 5470

_Source: docs/sketchpad.html_

Skip to content


SYSEN 5470 · Sketchpad


# Draw It BeforeYou Code It.


Every case study includes a sketchpad activity — hand\-drawn, keyboard\-free, deliberately slow. Drawing forces the concept into your head before syntax can hide it. **Your sketchpad is a required piece of equipment for this course.**


✏️
**Why sketch?** You can copy\-paste working code without understanding it. You can run a betweenness function without knowing why one node sits between others. You cannot draw a network you don't understand. The sketch is a forced pause — a 15\-to\-30\-minute interval where the only thing happening is comprehension. After the sketch, the code lab feels like execution instead of guessing.


### 🎒 Gear list


* One sketchpad or pad of plain paper
* A pen you like writing with
* Two colors (any two — red \& black is fine)
* Your phone, for photographing the finished sketch


The Eleven Prompts — one per lab


🕸️


### Sketch 01 · Map your network


Identify
\~20 min


 Pick a system you know well — your team, your supply chain, your transit commute, a household. Draw **five to twelve nodes** with edges between them. Label each node. Label at least two edges with what flows along them (information, goods, money, trust). Use one color for directed edges, another for undirected.

PurposeDismantles the assumption that "real systems are too messy to model." If you can draw it, you can analyze it.
* Five to twelve nodes, labeled
* Edges with explicit direction (arrowheads)
* Two edge labels naming what flows


📊


### Sketch 02 · Predict the bottleneck


Measure
\~25 min


 Look at your Sketch 01\. Circle the node you think has the **highest degree** (most edges). Now circle the node you think has the **highest betweenness** (sits on the most shortest paths). If they're the same node, your network is too simple — add edges until they diverge.

PurposeDismantles the "busiest \= most critical" misconception before the code lab gives you the data.
* Two circled nodes (degree, betweenness) on Sketch 01
* A one\-sentence prediction: which node, if removed, breaks the most paths


📐


### Sketch 03a · Two null distributions — Bluebikes case


Infer
\~20 min


 Sketch the five Bluebikes neighborhoods as labeled circles. Mark each as high\-income (one color) or low\-income (other color). Draw the arrows you'd *expect* to be heaviest. Now sketch two histograms side by side: an "unblocked permutation" null and a "block permutation" null. Mark the observed value with a vertical line. Which test would call the observed pattern significant, and which wouldn't?

PurposeSurfaces the gap between "random shuffle" and "structurally plausible shuffle" — the heart of network\-aware inference. Lab\-specific version.
* Five labeled nodes, color\-coded by group
* Expected heavy edges (arrows)
* Two histograms with the observed value drawn in


📐


### Sketch 03b · Two null distributions — your network


Infer
\~25 min


 Now substitute **your own network and your own grouping variable**. Sketch the nodes as labeled circles, colored by your grouping (gender, region, tier, faction, role — whatever makes sense for your project). Draw the arrows you'd expect to be heaviest based on your domain knowledge. Then sketch the same two histograms: an unblocked permutation that ignores groups, and a block permutation that preserves within\-group structure. Mark the observed value. Which null is the right one for *your* question?

PurposeForces you to define the grouping that matters for your project, and to commit to a null hypothesis before running it. Project\-track students do this version in their project week.
* 5–15 labeled nodes from your network, colored by your grouping
* Expected heavy edges, with a one\-sentence "why" in the margin
* Two histograms with the observed value, plus a one\-line interpretation


🚦


### Sketch 04 · Pick where to add a road


Predict
\~25 min


 Draw a transit or supply network with at least **three components** that are not yet connected. Pick *one* edge you could add. Predict which metric — average path length, diameter, number of components, total flow — will change most, and by roughly how much. Now pick the *wrong* edge: one that *looks* like a good addition but isn't.

PurposeTrains your eye for counterfactual graph mutation before the code lab automates it.
* 3\+ disconnected components
* Two candidate edges, with a written prediction for each


🧩


### Sketch 05 · Draw the seams


Measure
\~20 min


 Take a 15\-to\-25 node graph (your own data, or a sketched one). Draw the **boundaries** you'd cut the graph along to separate it into 2–4 communities. Now find one node that sits *on* a boundary — a bridge between communities. What would happen to your cluster assignments if that node disappeared?

PurposeInternalizes the difference between modular structure and structural holes before the algorithm finds them for you.
* 15\+ nodes
* 2–4 cluster boundaries (drawn as loops or dashed lines)
* One identified bridge node


🤖


### Sketch 06 · Two\-hop neighborhood


Predict
\~20 min


 Pick a node in your sketched supply network. Highlight its **two\-hop neighborhood** — every node reachable within two edges. List the features of those neighbors (size, country, delay rate, sole\-source status). Now write a one\-sentence prediction: based *only* on its neighborhood (not its own attributes), is this node at higher or lower risk of disruption?

PurposeMakes the message\-passing intuition visible. The GNN does the same thing, just numerically.
* One highlighted center node
* Its two\-hop neighborhood shaded
* A list of 4–6 neighbor features and a one\-line risk prediction


🗺️


### Sketch 07 · One chart, three audiences


Identify
\~30 min


 Pick one network insight from a previous lab (a bottleneck, a community, a risk score). Sketch the **same insight three times** — once for a technical peer, once for a non\-technical executive, once for a public\-facing dashboard. What changes? What stays? Mark in red anything you'd remove for the public version.

PurposeForces the recognition that "good visualization" isn't a property of a chart — it's a property of a chart\-audience pair.
* Three versions of the same insight, in three labeled boxes
* Red marks where the public version is simplified


🗄️


### Sketch 08 · Plan the join


Identify
\~25 min


 You have three tables: **nodes** (id, label, group), **edges** (from, to, weight, time), and a **node\-attributes** table (id, country, financial\_score). Draw the schema as boxes with arrows. Mark the keys you'd join on. Now sketch the *output* table the GNN needs — one row per node per timestep — and trace, with arrows, where every column comes from.

PurposeMakes the data\-wrangling step concrete. Edge lists are easy. Joining node attributes back to edge\-context features is where most students stall.
* Three table boxes with column names
* Join keys marked
* An output table sketch with column\-provenance arrows


🧠


### Sketch 09 · Trace a forward pass


Predict
\~25 min


 Draw a five\-node directed graph of your own. Label each node with a feature **x ∈ \[0, 1]** and a ground\-truth label **y ∈ {0, 1}**. By hand, compute the first GNN aggregation step: **x̃ᵢ \= xᵢ \+ mean(neighbors' x)**. Then pick small weights (w₁ \= 0\.5, w₂ \= 0\.4, b \= 0\.1\), push x̃ through ReLU and Sigmoid, and write the final ŷᵢ for each node. Where in the math does the graph structure actually show up?

PurposeDemystifies the GNN. The neighborhood aggregation step is the only thing that distinguishes a GNN forward pass from a plain\-NN forward pass — and you'll feel it the moment you do the arithmetic.
* Five nodes, each labeled with x and y
* x̃ value circled at each node after one aggregation step
* Final ŷ written next to each node


🔗


### Sketch 10 · Sketch the pipeline


Identify
\~20 min


 Pick three real tables from any system you know (your work data, a course dataset, anything). For each table, draw a box with column names. Then identify, in writing next to your boxes: **(a) the join key**, **(b) what the column collision will be after the first join** (which two columns will share a name?), and **(c) what you'll rename it to**. Finally, write the final pipeline as a sequence of verbs — `left_join → rename → mutate` or `merge → rename → assign`.

PurposeSurfaces the column\-collision moment *before* it becomes an error message in the lab. The rename step is the part everyone forgets — sketching it forces you to remember.
* Three table boxes with column names
* Arrows marking join keys
* The two columns that will collide after the first join, with the new names you'll give them
* The final pipeline as 4–6 verbs in sequence


🗺️


### Sketch 11 · Lose detail to gain insight


Identify
\~25 min


 Pick a many\-node network — real or sketched, 20\+ nodes. Draw it three times at three zoom levels: **(1\)** all nodes individually, **(2\)** grouped into 5–8 categories of your choice, **(3\)** grouped into 2–3 high\-level buckets. For each zoom level, write one insight you can see at *that* level that you couldn't see at the others. Mark with an arrow the level that best supports your one\-sentence engineering recommendation.

PurposeInternalizes that aggregation isn't "losing data" — it's choosing what to make visible. The level that best supports the recommendation is rarely the most detailed one.
* The same network at three zoom levels, side by side
* One insight written under each level
* An arrow marking the level that supports your engineering recommendation
* The one\-sentence recommendation itself


Sharing \& Submission

 Photograph your finished sketch and upload it with your weekly lab submission. We don't grade artistic quality — we grade whether the sketch shows you understood the structure before you wrote the code. A sketch that just copies the prompt back gets a redo; a sketch with a wrong prediction that you then test in the lab and refute is exactly what we're looking for.


**SYSEN 5470 · Sketchpad Prompts Library**

 Cornell Engineering · Summer 2026 · The whole library, including prompts for case studies not yet built, is here as a preview.

---

# About · SYSEN 5470

_Source: docs/about.html_

Skip to content


SYSEN 5470 · About


# Who's TeachingAnd Why This Course.


A 3\-week, 3\-credit summer intensive built for working professionals and engineering grads who'd rather learn one thing well than survey eight things badly. Network science is taught the way an engineer needs it: stakes\-first, with the naive alternative in plain view.


Your Instructor

![Tim Fraser headshot](images/instructor.jpg)

## Tim Fraser, PhD


Assistant Teaching Professor · Computational Social Scientist · Systems Engineering Program, Cornell University
Computational social scientist working at the intersection of resilience, mobility, and applied data science. Tim teaches network analysis, statistical inference, and systems engineering in the Systems Engineering Program at Cornell — and builds the kinds of tools and case studies he wishes existed when he was a student.


Research focus: how interdependent networks — transit systems, organizations, evacuation routes, and other webs of interconnected actors — fail, recover, and can be designed to do both better.


→ tmf77@cornell.edu
→ github.com/timothyfraser


Course Philosophy


🎯
#### Skills, not survey


Four transferable analytical skills you'll take into your engineering practice — not a buffet of definitions you'll forget. Every unit is anchored to one of them.


⚖️
#### Naive vs. network\-aware


Every lab opens with what most engineers reach for first — and where it falls short. The contrast is the lesson.


✏️
#### Sketch before code


Hand\-drawn activities force the concept into your head before syntax can hide it. Your sketchpad is a required piece of equipment.


📅
#### Work\-life friendly


100% asynchronous. Assignments due Monday mornings at 9 AM. Short videos. Extensions for SYSEN 5940 in\-person students.


🛠
#### Real data, day one


Supply chains, mobility networks, supplier\-risk feeds — not toy graphs. The case studies are the curriculum.


🚪
#### No prerequisites


R or Python welcome but not required. Quickstart tutorials are built into the course. Bring curiosity and a sketchpad.


⚖ AI Use Policy
### What AI is for in this course (and what it isn't).


The short version: AI is welcome for **syntax and debugging**, not for **writing your reports or answering reflections**. The course is about your thinking; reports are how we see your thinking.


#### You may use AI for


* Syntax help and debugging
* Explaining error messages
* Clarifying readings or lab concepts
* Generating example data


#### You may not use AI for


* Writing your project report prose
* Answering Learning Checks
* Writing reflections or interpretation prompts


The **Course Companion** (NotebookLM) is grounded in this course's own materials and is the recommended way to ask AI questions during the course. It will not write your reports for you, by design.


Read the full AI Use Policy →


Common Questions

Who is this course for?
Cornell graduate students from any program, plus full\-time working professionals admitted as graduate\-at\-large. If you work with interdependent systems — supply chains, infrastructure, organizations, transit, software, healthcare — this course is built for you.


Do I need to know R or Python?
No. Some prior experience helps but is not required. Quickstart tutorials are in the course, and the labs are scaffolded so a stats\-naive student can hit the floor and an advanced student has room to extend.


How much work per week?
Roughly 8–10 hours per week. One \~4\-hour weekend block per unit (video, reading, sketch, code, check) plus a short Monday\-morning homework on your own data.


What's the deal with SYSEN 5940?
If you're taking SYSEN 5940 in\-person that same week, extensions and flexibility are available so you can integrate both. Email Tim and we'll work it out.


Where can I read more before enrolling?
Start with the Syllabus, then poke at the live Case Studies. The labs are open — you don't need to enroll to try them.


## Questions? Email Tim.


The fastest way to know whether this course is right for you is to ask.


SYSEN 5470
June 22 – July 10, 2026
3 Credits

Email tmf77@cornell.edu


**SYSEN 5470 · Network Science and Applications for Systems Engineering**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu
 · instructor →

---

# SYSEN 5470 – Network Science and Applications for Systems Engineering

_Source: docs/flyer.html_

Skip to content

![Network Science and Applications for Systems Engineering banner](https://github.com/timothyfraser/netsci/blob/f495e6960b9e917704851f820c1cfeea36ae3ea8/docs/images/banner_bottom.png?raw=true)

Cornell Engineering
Summer 2026
3 Credits
Graduate
Asynchronous

SYSEN 5470


# Network Scienceand Applicationsfor Systems Engineering


 Supply chains collapse. Power grids fail. Logistics break down. Engineers who understand networks can see these failures coming — and design systems that survive them. Learn to think in networks in just **3 weeks**.


3
Weeks · 3 Credits


8
Real\-World Case Studies


0
Coding Experience Required


∞
Networks Around You


What You'll Learn


🕸️

**Network Fundamentals**
Nodes, edges, direction, weighting, small\-world phenomena


📊

**Centrality \& Criticality**
Identify bottlenecks, hubs, and vulnerabilities in any system


🤖

**AI \& Machine Learning**
Neural networks, graph neural nets, and ML for network inference


📐

**Network Statistics**
Permutation tests, bootstrap, and causal inference on networks


🚦

**Routing \& Optimization**
Solve real flow and routing problems in logistics and transit


🧩

**Clustering \& Communities**
Detect structure in large\-scale networks automatically


🗺️

**Visualization**
Communicate network insights with beautiful, interactive graphics


🗄️

**Big Network Data**
Work with millions of edges using databases and smart sampling


Case Studies

🚲 Bike\-Share Mobility (Boston)
🌀 Hurricane Evacuation Networks
📦 Supply Chain Risk
⚡ Power Grid Resilience
🚇 Urban Transit Systems
🏭 Crisis Stakeholder Networks
💻 Data Center Connectivity
🏗️ Organizational Networks \& DSMs


How It Works
* 100% asynchronous classes — learn on your schedule
* Assignments due at end of each weekend
* Hands\-on coding labs in R or Python (you choose)
* Sketchpad exercises — draw networks by hand
* Short videos \+ interactive tutorials
* Real datasets from the start, Day 1
* Designed for full\-time working professionals
* Extensions welcome for SYSEN 5940 in\-person session participants!


Your Instructor

![Tim Fraser](https://avatars.githubusercontent.com/u/50339247?s=400&u=6f542f60740f5288c64de51544255c82b010e822&v=4?raw=true)

### Tim Fraser, PhD


Assistant Teaching Professor · Computational Social Scientist · Cornell University

 Research on resilience, mobility networks, and computational social science.

tmf77@cornell.edu


## Enroll This Summer!


No prior coding or graph theory experience required. Just bring your curiosity — and a sketchpad.


SYSEN 5470
June 22 \- July 10, 2026
3 Credits


 Prerequisites: None. Some prior R or Python experience helpful but not required.

**This course is designed for graduate students at all coding levels.**

 Questions? Contact **tmf77@cornell.edu**

---

# Assignments · SYSEN 5470

_Source: docs/assignments.html_

Skip to content


SYSEN 5470 · Assignments


# A Weekly Rhythm.Three Weeks. One Report at a Time.


Every Monday at 9 a.m., you submit the same four things from the previous week — a sketch, a case\-study check, a code check, and your project case study. Rinse, repeat, three times. By the end, you'll have shipped three short reports applying network science to a problem you chose.


**Submission deadline**
Every Monday at 9:00 a.m.


⏱
**Why a steady weekly cadence?** Network science is a habit, not a one\-shot performance. The Monday cadence is short enough that you'll never have a week's worth of work to catch up on, and long enough that you can sit with hard ideas before producing something. You're encouraged to submit earlier — there's no bonus for going to the wire.


What you submit each week

✏️

Item 1 · Sketchpad
### Sketches for the current week


Hand\-drawn sketches for every sketchpad prompt assigned to the current week. Photograph and upload. The sketch precedes the code — it's how you check that you understand the structure before syntax can hide it.


🧪

Item 2 · Case Study Learning Checks
### One LC per case study from last week


For every interactive case study lab assigned to the previous week, submit the in\-lab Learning Check answer.


⌨️

Item 3 · Code Learning Checks
### One LC per `example.R` / `example.py` from last week


For every case study you completed last week, you also run the `example.R` or `example.py` script in the matching `code/` folder. Each script prints a single numeric (or string) answer at the bottom — that's your code Learning Check answer. Pick either track (R or Python). You don't need to do both.


📄

Item 4 · Project Case Study
### Your project code \& report for this week's case study


You pick **3 out of 11** case studies to do as project case studies (one per week). For each one you submit (a) a `project.R` or `project.py` that runs your full analysis on a network *you* chose, and (b) a 2\-page\-minimum report in your own words. See the Project section below for the full spec.


Project case studies

 The project is a big chunk of your grade. Over three weeks you'll
 pick **3 of the 11** case study methods, apply each
 one to a network you chose, and write a short report. The point
 isn't to redo the example script with different data — it's to
 pose a meaningful question, justify your operationalization, run
 a defensible analysis, and report your results as quantitative
 quantities of interest in prose. Each report should comfortably
 fill at least two pages.


How your project is graded — the rubric

 Each project case study is scored against the skill it primarily exercises — Identify, Measure, Infer, or Predict. Four tiers per skill. Aim for *Meets*; *Exceeds* takes the same time but more care.


### Identify


Make the network legible

Not yet
Node, edge, and weight are undefined or contradictory.
Approaching
Defined but not justified — could be defended in five different ways.
Meets
Node, edge, weight, and data source are stated and justified in plain prose.
Exceeds
Reports an alternative encoding that was considered and rejected, with reasoning.


### Measure


Compute the right number

Not yet
One metric reported with no argument for it.
Approaching
Right metric for the question, but no robustness check or alternative.
Meets
Metric is argued from the question. Sensitivity or alternative metric appears.
Exceeds
Two metrics compared; honest discussion of where they disagree and why.


### Infer


Say what's real, not just observed

Not yet
A point estimate with no comparison.
Approaching
Compared to a null, but the null is unjustified (e.g. unblocked when blocks matter).
Meets
Null model justified, p\-value or CI reported, claim is no stronger than the test supports.
Exceeds
Two nulls compared, with explicit discussion of which is right for the question.


### Predict


Use the network to anticipate

Not yet
Model fits but its decision\-relevance is unstated.
Approaching
AUC or accuracy reported, but no baseline, threshold, or operational framing.
Meets
Compared against a non\-network baseline; threshold or operating point chosen and defended.
Exceeds
Reports where the model fails, and how a stakeholder would catch it before acting on it.


### Every project report must include


* The question, in one sentence.
* How you operationalized the network — what's a node, what's an edge, what's an edge weight, where did the data come from.
* The procedure you ran, in plain language, in order.
* Your results stated as *numbers in prose*, with at most 1–2 supporting figures and 1 table.
* What this tells you, and what it doesn't (2–3 sentences).


⚖ AI Use Policy
### What AI is for in this course (and what it isn't).


The short version: AI is welcome for **syntax and debugging**, not for **writing your reports or answering reflections**. The course is about your thinking; reports are how we see your thinking.


#### You may use AI for


* Syntax help and debugging
* Explaining error messages
* Clarifying readings or lab concepts
* Generating example data


#### You may not use AI for


* Writing your project report prose
* Answering Learning Checks
* Writing reflections or interpretation prompts


The **Course Companion** (NotebookLM) is grounded in this course's own materials and is the recommended way to ask AI questions during the course. It will not write your reports for you, by design.


Read the full AI Use Policy →


### Hard requirements


* The *writing must be your own*. See the AI Use Policy — AI can help with code; the prose has to come from you.
* Your network must have **at least 100 nodes**. Networks of **1,000\+ nodes are strongly preferred** — they force you to handle the difficulty of real\-world data, which is the whole point of the course.
* If you haven't decided on a network by the *end of week 1*, contact the instructor and one will be manufactured to fit your field or chosen industry.
* Submit both the script (`project.R` or `project.py`) and the report (PDF preferred). The script must run end\-to\-end on the dataset you submit alongside it.


📄

### What does a project report actually look like?


One real exemplar so you know what 2 pages of "numbers in prose" actually means. Open it on a phone or laptop, skim once before you start your own. The point is the *shape* of the analysis, not the specific topic — yours should look like this on the page.


⬇ Download sample report (PDF)
↗ Open in new tab

Source markdown lives at `assignments/sample-report.md` if you want to read the raw text.


Self\-grade before you submit

 Click through these before you hit submit. Most missed\-point situations are catches this list would have flagged. The **Copy** button writes a paste\-able status block to your clipboard — paste it into the project box on Canvas so Tim can see what you flagged for yourself.


 Each case study folder under `code/` has a dedicated
 *Your Project Case Study* section in its README, with 3
 suggested project questions to pick from. You don't have to use
 one of the suggestions — they're starting points.


| \# | Case study | Skill | Interactive lab | Code folder (GitHub) |
| --- | --- | --- | --- | --- |
| 01 | Build a Network | Identify | Lab | Code \& README |
| 02 | Network Joins | Identify | Lab | Code \& README |
| 03 | Aggregation | Identify | Lab | Code \& README |
| 04 | Centrality \& Criticality | Measure | Lab | Code \& README |
| 05 | Supply Chain Resilience | Measure | Lab | Code \& README |
| 06 | DSM Clustering | Measure | Lab | Code \& README |
| 07 | Network Permutation | Infer | Lab | Code \& README |
| 08 | Sampling Big Networks | Identify | Lab | Code \& README |
| 09 | Counterfactual Monte Carlo | Predict | Lab | Code \& README |
| 10 | GNN by Hand | Predict | Lab | Code \& README |
| 11 | GNN \+ XGBoost | Predict | Lab | Code \& README |


Office hours \& meetings

☎️
You're required to meet with the instructor for **three virtual office\-hour sessions** across the course. These count toward your activities grade. They're informal — bring a question, a stuck spot, or a project you're considering. Sign up via the link in the course site.


Final presentation

🎤
At the end of the term, you give a short presentation on your **strongest of the three project case studies**. We'll use these to share what worked across cohorts. Format and length are confirmed in the course site once enrollment closes.


**SYSEN 5470 · Assignments**

 Cornell Engineering · Summer 2026 · Three Mondays, three reports, one network you'll know inside\-out.

---

# Calendar · SYSEN 5470

_Source: docs/calendar.html_

Skip to content


SYSEN 5470 · June 22 – July 10, 2026


# Day\-by\-DayPacing.


The syllabus tells you what the course covers. This page tells you when to do it. Built around the rhythm a full\-time\-working student actually uses: a long weekend block for each lab, with the Monday\-9am submission at the end of every week. **The weekend blocks are when most of the work happens** — protect them.


Weekday — short evening touch
Weekend — the main work block
Monday 9 AM — week's submission due


Week 01
## Think Like a Graph


Jun 22 – Jun 28, 2026
Nodes, edges, small\-world phenomena. Three labs: Build\-a\-Network, Network Statistics, Centrality.


Mon Jun 22day 1

**Course opens.** Read the syllabus, skim the Help hub, run Setup if you haven't. \~30 min total.


Tue Jun 23day 2

🕸️ Build\-a\-Network Watch the lab video, read Barabási Ch. 1–2\. \~45 min.


Wed Jun 24day 3

**Sketch 01 · Map your network.** 20 min sketchpad, no keyboard. Open the prompt →


Thu Jun 25day 4

📐 Network Statistics Read Farine 2017 (null models). Skim Bluebikes lab intro. \~30 min.


Fri Jun 26day 5

📊 Centrality Read Barabási Ch. 3 and Ch. 8\. \~30 min. Light evening — protect Saturday.


Sat Jun 27day 6

Weekend block**Run the three labs.** Plan \~4 hours. Open the Build\-a\-Network lab first, then Network Statistics, then Centrality. Sketch 02 \+ 03a in between.


Sun Jun 28day 7

Weekend blockWrite your three Learning Check answers and the one\-page reflection. Photograph your sketches. **Stage the Monday submission.**


Mon Jun 299 AM

Due 9 AM**Week 1 submission.** Three sketch photos · three LC answers · one reflection. See Assignments for the exact spec.


Week 02
## Find What Matters


Jun 29 – Jul 5, 2026
Critical structure. Four labs: Supply Chain, Routing, Clustering, Aggregation.


Mon Jun 29day 8

 Submission done. Read this week's syllabus block, watch the supply\-chain video. \~30 min.


Tue Jun 30day 9

📦 Supply Chain Read Barabási Ch. 10 (cascades). \~30 min.


Wed Jul 01day 10

🚦 Routing Skim Bertsekas reference chapter. **Sketch 04 · Pick where to add a road.**


Thu Jul 02day 11

🧩 Clustering Read Barabási Ch. 9 (communities). **Sketch 05 · Draw the seams.**


Fri Jul 03day 12

🗺️ Aggregation Read Bellantuono 2025 (accessibility via transit). **Sketch 11 · Lose detail to gain insight.** Light evening.


Sat Jul 04day 13

Weekend block**Run the four labs.** Heavier than week 1 — plan \~5 hours. Bring tea. Holiday in the US; some students prefer to start Friday evening and finish Sunday.


Sun Jul 05day 14

Weekend blockWrite LC answers, reflection, and (if you picked one of these for the project) your *first project case study* — code \+ 2\-page report.


Mon Jul 069 AM

Due 9 AM**Week 2 submission.** Four sketch photos · four LC answers · one reflection · *(if applicable)* your first project case study.


Week 03
## Move \& Predict


Jul 06 – Jul 10, 2026
Forecasting and big data. Four labs: GNN by Hand, GNN \+ XGBoost, Sampling, Joins. Plus the final project submission.


Mon Jul 06day 15

 Submission done. Watch this week's intro video. 🧠 GNN by Hand


Tue Jul 07day 16

🤖 GNN \+ XGBoost Read Khan 2025 (ML for network inference). \~30 min.


Wed Jul 08day 17

🗄️ Sampling Skim Easley \& Kleinberg §2\.4 (network datasets). **Sketch 09 · Trace a forward pass** for the GNN labs.


Thu Jul 09day 18

🔗 Joins **Sketch 10 · Sketch the pipeline.** Light evening — final crunch starts tomorrow.


Fri Jul 10day 19

Final\-week blockLast labs (GNN by Hand, GNN \+ XGBoost, Sampling, Joins). Wrap your final project case study or two. **Final presentations** happen this day for cohort members who attend — see Assignments.


Mon Jul 139 AM

Final due 9 AM**Week 3 \+ final project submission.** Remaining sketches and LCs · two reflections (this week and a course\-level retrospective) · your *two remaining project case studies* with reports. Grades close out the week after.


**Extensions for SYSEN 5940 in\-person students:** if you're juggling 5940 in the same week, email Tim before the Monday deadline and we'll work out a revised due date. The async structure makes this easy; just communicate early.


**SYSEN 5470 · Calendar**

 Cornell Engineering · Summer 2026 · tmf77@cornell.edu

---

# Promo

_Source: docs/promo.md_

# 🕸️ Your Network Science Summer 

## (3 credits, 0 coding experience needed) June 22 - July 10, 2026!

### TLDR

Why networks matter: 🤔 Classical stats assume independence. Networks laugh at independence. If you analyze networked data with traditional methods, you'll get false positives, miss real patterns, and make bad decisions. 
This course fixes that. Your supply chain (and your boss) will thank you!

- ✅ 3 weeks. 3 credits. Summer intensive.  🎥  Short Asynchronous Videos (learn on your time).  
- ✅ No prior coding experience required. Quickstart tutorials in R/Python available in this course!  
- ✅ 8 case studies: Supply chains 📦 · Power grids ⚡ · Transit systems 🚇 · Organizational networks 🏗️ · Data centers 💻 · Crisis response 🏥   ·  Bike-share 🚲 · Hurricane evacuation 🌀 · 
- ✅ Hands-on:  💻  Code +  ✏️  sketching +  📊  thinking like an engineer.  
- ✅ Work-life friendly. Assignments due Monday mornings @ 9 AM.

### BONUS

🎓  Taking SYSEN 5940 in-person that week? Integrate! Extensions and flexibility available to encourage participation in SYSEN 5940.

See you in June! 🕸️
- Tim Fraser (your professor)

---

# Readme

_Source: docs/images/README.md_



---

# Readme

_Source: docs/playground-data/README.md_

# Playground Sample Networks

Small network datasets bundled with the coding playgrounds. Each network is a
pair of CSV files: one for nodes (with attributes), one for edges (with
weights). Designed to be small enough to fit comfortably in WebR or Pyodide's
in-browser memory and to load instantly.

Both `playground-r.html` and `playground-py.html` fetch these CSVs into the
WASM virtual filesystem when you pick a sample from the loader dropdown.

| key | nodes | edges | description |
|---|---|---|---|
| `karate` | 34 | 78 | Zachary's karate club (1977). Faction = `instructor` / `officer`. The canonical small social network. |
| `lakeside` | 15 | 19 | The 15-station Lakeside Bikeshare network from the **Counterfactual Monte Carlo** lab. Edges weighted by Q1 ridership. |
| `riverdale` | 18 | 21 | The 18-station Riverdale Metro & Bus network from the **Centrality & Criticality** lab. Edges weighted by typical riders/day. |
| `supply-chain` | 16 | 30 | The 16-factory supply chain from the **Network Joins** lab. Three tiers (Tier 1 final assembly, Tier 2 subassembly, Tier 3 raw). Volume-weighted shipment lanes. |

## Columns

### Nodes

- `karate`: `id, name, faction`
- `lakeside`: `id, label, zone, type`
- `riverdale`: `id, label, zone, type`
- `supply-chain`: `node_id, name, region, tier, capacity_units`

### Edges

- `karate`: `source, target, weight` (weight is always 1 — Zachary's network is unweighted)
- `lakeside`: `source, target, weight` (ridership)
- `riverdale`: `source, target, line, weight` (line ∈ red/blue/green/yellow/bus; weight = ridership)
- `supply-chain`: `from_id, to_id, lane, volume_units`

## Provenance

All datasets are synthetic or public:

- **Karate** is the canonical Zachary (1977) edge list.
- **Lakeside, Riverdale, Supply-chain** are the toy networks used in our own labs. They are not real data.

---

