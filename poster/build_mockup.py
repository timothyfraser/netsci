#!/usr/bin/env python3
"""Build the 40x30in poster as ONE self-contained HTML file with a live control sidebar.

The sidebar is screen-only: it never prints. Ctrl/Cmd+P exports the poster at true
40x30in. Every figure is embedded four times (one per theme) so the toggles work offline.
"""
import base64, io, pathlib
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ASSETS, SHOTS = HERE / "assets", HERE / "shots"
THUMBS = pathlib.Path("/home/user/netsci/data/projects")
OUT = HERE / "poster-mockup.html"

BAND_IN = 2.361          # the Duffield template's red band, measured off the artwork
THEMES = ["white", "grey", "redlight", "red", "reddark", "orig"]


def uri(img, fmt="JPEG", quality=80):
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
        mime = "image/jpeg"
    else:
        img.save(buf, "PNG", optimize=True)
        mime = "image/png"
    return f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode()}", len(buf.getvalue())


def load(path, max_w=None, **kw):
    im = Image.open(path)
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    u, n = uri(im, **kw)
    print(f"  {path.name:22s} {im.size[0]}x{im.size[1]:<5} {n/1024:7.0f} KB")
    return u


def lab_cut_row():
    """Find a row where BOTH panels are between cards, so the crop never slices a card."""
    a = np.asarray(Image.open(SHOTS / "lab-orig.png").convert("RGB")).astype(int)
    H, W = a.shape[:2]
    ml = a[:, :1230, :].max(axis=(1, 2))
    mr = a[:, 1230:, :].max(axis=(1, 2))
    left_end = max((y for y in range(H) if ml[y] > 90), default=H - 1)
    run = 0
    for y in range(left_end + 5, H):
        run = run + 1 if (ml[y] < 90 and mr[y] < 90) else 0
        if run >= 25:
            cut = y - run + 22
            print(f"  lab crop row {cut} (left panel ends {left_end}) aspect {W/cut:.2f}")
            return cut
    print("  lab crop fallback")
    return H


print("embedding assets:")
CUT = lab_cut_row()
FIGS = {t: {} for t in THEMES}
for t in THEMES:
    lab = Image.open(SHOTS / f"lab-{t}.png")
    lab = lab.crop((0, 0, lab.width, min(CUT, lab.height)))
    tmp = SHOTS / f"_lab-{t}-crop.png"
    lab.save(tmp)
    FIGS[t]["lab"] = load(tmp, max_w=2300, quality=80)
    FIGS[t]["viz"] = load(SHOTS / f"viz-{t}.png", max_w=1900, quality=80)
    FIGS[t]["pg"] = load(SHOTS / f"pg-{t}.png", max_w=2300, quality=80)

BG = load(ASSETS / "background.png", max_w=2880, quality=90)
HEAD = load(ASSETS / "instructor.jpg", max_w=560, quality=88)
QR_SITE = load(ASSETS / "qr-site.png", fmt="PNG")
QR_VIZ = load(ASSETS / "qr-visualizer.png", fmt="PNG")
QR_HOME = load(ASSETS / "qr-home.png", fmt="PNG")
STAMP_NAMES = ["power-grid", "amazon-last-mile", "semiconductor-supply", "campus-contact"]
STAMPS = [load(THUMBS / n / "thumb.png", max_w=340, quality=82) for n in STAMP_NAMES]

lab_ar = round(Image.open(SHOTS / "_lab-white-crop.png").width / Image.open(SHOTS / "_lab-white-crop.png").height, 3)
print(f"  lab aspect {lab_ar}")

# ---------------------------------------------------------------- content
STATS = [("11", "interactive labs"), ("21", "project datasets"), ("2", "languages, one lesson"),
         ("17", "packages, zero installs"), ("$0", "servers or hosting")]

# (lead, always-shown, standard-extra, detailed-extra)
STEPS = [
    ("Encode rules", "Teaching style, glossary, dataset standards.",
     "", " Written once, reused by every artifact after."),
    ("Draft with AI", "A lab, a dataset, or lesson code.",
     "", " The instructor sets the teaching goal, not the markup."),
    ("Verify automatically", "",
     " Browser tests; R and Python must agree.", " A lab that fails its own learning check never ships."),
    ("Instructor reviews", "Design, features, tone, and accuracy — before anything ships.",
     "", " Every artifact is read by a human, not just generated."),
    ("Ship free with GitHub Pages", "",
     " CI rebuilds the student repo and study companion.", " No server to run, nothing to renew each term."),
]

GETS = [
    ("Real code, no setup.", "R and Python in the browser.", " No install, no accounts, any device."),
    ("Labs that push back.", "Metrics move as you edit.", " Remove a station and watch the network answer."),
    ("Explore, then code.", "Export the script you clicked.", " The visual analysis becomes a runnable file."),
    ("A tutor that asks.", "Socratic AI, never answers.", " Available all term, at no cost to students."),
]

CAPTIONS = {
    "lab": ("Case-study lab.", "Remove a station and every metric updates live.",
            " Learning-check answers are recomputed from the rendered network, so they cannot drift."),
    "pg": ("Coding playground.", "A full R or Python interpreter in the browser tab, via WebAssembly.",
           " Students load a course dataset and plot it without installing anything."),
    "viz": ("Network Visualizer.", "Click through failure cascades and counterfactuals on a 300-node grid.",
            " Then export the script that reproduces every click."),
}

PROBLEM = ("Students thrive with hands-on interactive exercises. But one production-quality "
           "lab is weeks of web engineering.",
           " A course needs dozens — plus datasets and code in two languages.")

stats_html = "\n".join(
    f'<div class="stat"><div class="stat-num">{n}</div><div class="stat-lab">{l}</div></div>' for n, l in STATS)
steps_html = "\n".join(
    f'<li><span class="step-n">{i}</span><div><b>{lead}.</b> {base}'
    f'<span class="lvl2">{std}</span><span class="lvl3">{det}</span></div></li>'
    for i, (lead, base, std, det) in enumerate(STEPS, 1))
gets_html = "\n".join(
    f'<li><b>{lead}</b> {base}<span class="lvl3">{det}</span></li>' for lead, base, det in GETS)
stamps_html = "\n".join(f'<img src="{u}" alt="">' for u in STAMPS)


def cap(key):
    lead, base, det = CAPTIONS[key]
    return f'<b>{lead}</b> {base}<span class="lvl3">{det}</span>'


figs_js = "{\n" + ",\n".join(
    "  " + t + ": {lab: '" + FIGS[t]["lab"] + "', viz: '" + FIGS[t]["viz"] + "', pg: '" + FIGS[t]["pg"] + "'}"
    for t in THEMES) + "\n}"

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>MTEI poster mockup — Interactive Course Labs, Built with AI</title>
<style>
  @page {{ size: 40in 30in; margin: 0; }}

  :root {{
    --accent:#B31B1B;
    --ink:#1c1c1c; --body:#333; --muted:#5a5a5a;
    --band:{BAND_IN}in; --pad:0.8in; --gap:0.55in;
    --ts:1;            /* text scale   */
    --fs:1;            /* figure scale */
    --zoom:0.28;       /* screen preview only */
    --card-bg:#ffffff; --card-line:rgba(0,0,0,.12); --card-shadow:0 3px 12px rgba(0,0,0,.10);
    --card-ink:#1c1c1c; --card-body:#333333; --card-h2:#B31B1B;
    --backing: rgba(255,255,255,0.90);   /* card colour, behind text over busy artwork */
    --page-ink:#1c1c1c; --title-color:#B31B1B;
    --page-color:#ffffff;
    --band-grad: linear-gradient(90deg,#B02327 0%,#C32529 45%,#E8575A 100%);
    --figw: calc(17.1in * var(--fs));
    --vizw: calc(11.6in * var(--fs));
    /* the text column never drops below this, however large the figures get */
    --leftw: max(7.9in, calc(38.4in - var(--figw) - var(--vizw) - 1.1in));
  }}
  * {{ box-sizing:border-box; }}
  html, body {{ margin:0; padding:0; background:#4a4a4a; }}

  /* ------------------------------------------------ sidebar (screen only) */
  #sidebar {{
    position:fixed; top:0; left:0; width:330px; height:100vh; overflow-y:auto; z-index:10;
    background:#1b1b1b; color:#eee; padding:18px 18px 40px;
    font:13px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    box-shadow:2px 0 14px rgba(0,0,0,.4);
  }}
  #sidebar h2 {{ margin:0 0 2px; font-size:17px; color:#fff; }}
  #sidebar .sub {{ color:#9d9d9d; font-size:12px; margin-bottom:16px; }}
  #sidebar fieldset {{ border:0; border-top:1px solid #333; margin:0 0 14px; padding:12px 0 0; }}
  #sidebar legend {{ font-size:11px; letter-spacing:.10em; text-transform:uppercase; color:#B31B1B;
                     font-weight:700; padding:0; }}
  #sidebar label {{ display:block; margin:7px 0; cursor:pointer; }}
  #sidebar input[type=range] {{ width:100%; }}
  #sidebar .row {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
  #sidebar .val {{ color:#9d9d9d; font-variant-numeric:tabular-nums; }}
  #sidebar select, #sidebar input[type=color] {{ width:100%; padding:5px; background:#2a2a2a;
      color:#eee; border:1px solid #444; border-radius:5px; }}
  #sidebar button {{ width:100%; padding:9px; margin-top:6px; border:0; border-radius:6px;
      background:#B31B1B; color:#fff; font-weight:700; font-size:13px; cursor:pointer; }}
  #sidebar button.ghost {{ background:#333; }}
  #sidebar .hint {{ color:#8d8d8d; font-size:11.5px; margin-top:10px; line-height:1.4; }}
  .combos {{ display:flex; flex-direction:column; gap:6px; }}
  #sidebar button.combo {{ width:100%; text-align:left; padding:8px 10px; font-size:12px;
      font-weight:600; background:#2c2c2c; border:1px solid #3d3d3d; border-radius:6px;
      color:#eaeaea; cursor:pointer; margin:0; }}
  #sidebar button.combo:hover {{ background:#3a3a3a; border-color:#B31B1B; }}
  .swatches {{ display:flex; gap:6px; margin:6px 0 2px; }}
  .swatches span {{ width:26px; height:22px; border-radius:4px; border:1px solid #555; cursor:pointer; }}
  #fitmsg {{ font-size:12px; padding:8px 10px; border-radius:6px; margin:6px 0 2px; line-height:1.35; }}
  #fitmsg.ok {{ background:#14331b; color:#8ee6a0; }}
  #fitmsg.warn {{ background:#3a1414; color:#ffb0a8; }}

  /* ------------------------------------------------ preview stage */
  #stage {{ margin-left:330px; padding:22px;
            width:calc(40in * var(--zoom) + 44px); height:calc(30in * var(--zoom) + 44px); }}
  .page {{
    width:40in; height:30in; overflow:hidden; position:relative;
    transform:scale(var(--zoom)); transform-origin:top left;
    padding: calc(var(--band) + 0.38in) var(--pad) 0.45in;
    display:flex; flex-direction:column;
    font-family: Arial, "Helvetica Neue", Helvetica, sans-serif; color:var(--ink);
    background:#fff url({BG}) no-repeat; background-size:40in 30in;
    -webkit-print-color-adjust:exact; print-color-adjust:exact;
  }}
  /* flat background: keep the template's branded band, drop the busy halftone */
  body[data-bg="color"] .page {{ background-image:none; background-color:var(--page-color); }}
  body[data-bg="color"] .page::before {{ content:""; position:absolute; inset:0 0 auto 0; height:var(--band);
      background-image:url({BG}); background-size:40in 30in; background-position:top left; }}


  /* backing cards so text stays readable over the template artwork */
  body[data-backing="on"] figcaption {{ background:var(--backing); padding:0.15in 0.22in;
      border-radius:11px; box-shadow:0 1px 6px rgba(0,0,0,.07); }}
  body[data-backing="on"] .author {{ background:var(--backing); padding:0.14in 0.26in 0.14in 0.16in;
      border-radius:16px; box-shadow:0 1px 6px rgba(0,0,0,.07); }}
  body[data-titleback="on"] h1 {{ background:var(--backing); padding:0.12in 0.26in;
      border-radius:16px; display:inline-block; }}

  /* ------------------------------------------------ header */
  header {{ display:flex; align-items:flex-start; gap:0.7in; }}
  header > div:first-child {{ flex:1 1 auto; min-width:0; }}
  h1 {{ margin:0; font-size:calc(144px * var(--ts)); line-height:1.03; font-weight:bold;
        color:var(--title-color); letter-spacing:-1px; max-width:26in; }}
  .author {{ margin-left:auto; flex:0 0 auto; display:flex; align-items:center;
             gap:0.30in; padding-top:0.06in; }}
  /* keep the block narrow enough that the title still sets on two lines */
  .author > div {{ max-width:6.6in; }}
  .author > img:not(.author-qr) {{ width:1.65in; height:1.65in; border-radius:50%; object-fit:cover;
                 border:4px solid #fff; box-shadow:0 3px 14px rgba(0,0,0,.22); }}
  /* sized to fill the author card without driving the header taller */
  .author-qr {{ width:calc(1.95in * var(--ts)); height:calc(1.95in * var(--ts));
                align-self:center; border-radius:4px; margin-left:0.30in;
                background:#fff; padding:0.06in; }}
  body[data-authorqr="off"] .author-qr {{ display:none; }}
  body[data-headshot="off"] .author > img:not(.author-qr) {{ display:none; }}
  .author .name {{ font-size:calc(52px * var(--ts)); font-weight:bold; line-height:1.12; color:var(--card-ink); }}
  .author .role {{ font-size:calc(37px * var(--ts)); color:var(--card-body); line-height:1.25; margin-top:0.05in; }}
  .author .meta {{ font-size:calc(30px * var(--ts)); color:var(--card-body); line-height:1.3; margin-top:0.05in; }}

  /* ------------------------------------------------ stats */
  .stats {{ display:grid; grid-template-columns:repeat(5,1fr); gap:var(--gap); margin:0.40in 0; }}
  body[data-stats="off"] .stats {{ display:none; }}
  .stat {{ background:var(--card-bg); border:1px solid var(--card-line); border-radius:14px;
           box-shadow:var(--card-shadow); padding:0.18in 0.30in; display:flex; align-items:center; gap:0.30in; }}
  .stat-num {{ font-size:calc(108px * var(--ts)); font-weight:bold; color:var(--card-h2); line-height:.96; }}
  .stat-lab {{ font-size:calc(37px * var(--ts)); font-weight:bold; color:var(--card-body); line-height:1.22; }}

  /* ------------------------------------------------ body grid */
  main {{ flex:1; display:grid; gap:var(--gap); min-height:0;
          grid-template-columns: var(--leftw) minmax(0, var(--figw)) minmax(0, var(--vizw)); }}
  .col {{ display:flex; flex-direction:column; gap:var(--gap); min-height:0; justify-content:space-between; }}
  .card {{ background:var(--card-bg); border:1px solid var(--card-line); border-radius:16px;
           box-shadow:var(--card-shadow); padding:0.32in 0.40in 0.36in; flex:0 0 auto; }}
  body[data-cards="none"] .card, body[data-cards="none"] .stat {{ background:transparent; border-color:transparent; box-shadow:none; }}
  h2 {{ margin:0 0 0.18in; font-size:calc(57px * var(--ts)); font-weight:bold; color:var(--card-h2);
        letter-spacing:1.2px; line-height:1.05; }}
  p {{ margin:0; font-size:calc(41px * var(--ts)); line-height:1.31; color:var(--card-body); }}
  .card b {{ color:var(--card-ink); }}

  ol {{ list-style:none; margin:0; padding:0; }}
  ol li {{ display:flex; gap:0.24in; font-size:calc(39px * var(--ts)); line-height:1.28; color:var(--card-body); }}
  ol li + li {{ margin-top:0.19in; }}
  .step-n {{ flex:0 0 auto; width:0.72in; height:0.72in; border-radius:50%; background:var(--card-h2);
             color:var(--card-bg); font-size:calc(44px * var(--ts)); font-weight:bold;
             display:flex; align-items:center; justify-content:center; }}
  ul {{ list-style:none; margin:0; padding:0; }}
  ul li {{ font-size:calc(39px * var(--ts)); line-height:1.28; color:var(--card-body);
           padding-left:0.42in; position:relative; }}
  ul li + li {{ margin-top:0.19in; }}
  ul li::before {{ content:""; position:absolute; left:0; top:0.20in; width:0.19in; height:0.19in;
                   border-radius:50%; background:var(--card-h2); }}

  figure {{ margin:0; flex:0 0 auto; }}
  figure img {{ width:100%; display:block; border-radius:10px; border:4px solid rgba(0,0,0,.18);
                box-shadow:0 5px 18px rgba(0,0,0,.22); }}
  figcaption {{ margin-top:0.15in; font-size:calc(36px * var(--ts)); line-height:1.26; color:var(--card-body); }}
  figcaption b {{ color:var(--card-ink); }}
  body[data-backing="off"] figcaption {{ color:var(--page-ink); }}

  .qr {{ display:flex; gap:0.5in; margin-top:0.22in; }}
  .qr div {{ flex:1; text-align:center; }}
  .qr img {{ width:calc(2.2in * var(--fs)); height:calc(2.2in * var(--fs)); display:block; margin:0 auto 0.12in; }}
  .qr span {{ font-size:calc(33px * var(--ts)); font-weight:bold; color:var(--card-body); }}
  body[data-qr="off"] #qrcard {{ display:none; }}
  .stamps {{ display:grid; grid-template-columns:repeat(4,1fr); gap:0.16in; margin-top:0.22in; }}
  .stamps img {{ width:100%; height:1.35in; object-fit:cover; display:block; border-radius:7px; }}
  body[data-datasets="off"] #datacard {{ display:none; }}

  /* detail levels */
  body[data-detail="1"] .lvl2, body[data-detail="1"] .lvl3 {{ display:none; }}
  body[data-detail="2"] .lvl3 {{ display:none; }}

  @media print {{
    html, body {{ background:#fff; }}
    #sidebar {{ display:none !important; }}
    #stage {{ margin:0; padding:0; width:40in; height:30in; }}
    .page {{ transform:none; }}
  }}
</style>
</head>
<body data-detail="1" data-cards="solid" data-bg="template" data-stats="on" data-qr="on"
      data-datasets="on" data-headshot="on" data-authorqr="on" data-backing="on" data-titleback="on" data-dark="off">

<div id="sidebar">
  <h2>Poster controls</h2>
  <div class="sub">Screen only — these never print. Press <b>Ctrl/Cmd + P</b> → Save as PDF for the real 40×30in poster.</div>

  <fieldset>
    <legend>Figure background</legend>
    <label><input type="radio" name="theme" value="white"> White</label>
    <label><input type="radio" name="theme" value="grey"> Light grey</label>
    <label><input type="radio" name="theme" value="redlight"> Light red</label>
    <label><input type="radio" name="theme" value="red" checked> Cornell red</label>
    <label><input type="radio" name="theme" value="reddark"> Dark red</label>
    <label><input type="radio" name="theme" value="orig"> Original (course neon)</label>
  </fieldset>

  <fieldset>
    <legend>Colour combos</legend>
    <div class="combos">
      <button class="combo" data-combo="default">Current — red figures, white cards, template art</button>
      <button class="combo" data-combo="a">A — dark red figures · light red cards · grey page</button>
      <button class="combo" data-combo="b">B — white figures · light red cards · Cornell red page</button>
      <button class="combo" data-combo="c">C — light red figures · white cards · dark red page</button>
      <button class="combo" data-combo="d">D — light red figures · dark red cards · white page</button>
    </div>
  </fieldset>

  <fieldset>
    <legend>Sizing</legend>
    <div class="row"><span>Figure size</span><span class="val" id="fsv">110%</span></div>
    <input type="range" id="fs" min="80" max="110" value="110">
    <div class="row"><span>Text size</span><span class="val" id="tsv">110%</span></div>
    <input type="range" id="ts" min="82" max="120" value="110">
    <div class="row"><span>Preview zoom</span><span class="val" id="zv">28%</span></div>
    <input type="range" id="zoom" min="10" max="60" value="28">
  </fieldset>

  <fieldset>
    <legend>Descriptive detail</legend>
    <label><input type="radio" name="detail" value="1" checked> Minimal — headlines only</label>
    <label><input type="radio" name="detail" value="2"> Standard</label>
    <label><input type="radio" name="detail" value="3"> Detailed — full sentences</label>
  </fieldset>

  <fieldset>
    <legend>Style</legend>
    <label>Card background<input type="color" id="cardcol" value="#ffffff"></label>
    <div class="swatches" id="cardsw"></div>
    <label><input type="checkbox" id="nocards"> No cards (text straight on the page)</label>
    <label>Accent colour<input type="color" id="accent" value="#B31B1B"></label>
    <label>True background (behind &amp; between cards)
      <select id="bg">
        <option value="template" selected>Duffield template artwork</option>
        <option value="#ffffff">White</option>
        <option value="#f7f7f7">Cornell light gray</option>
        <option value="#fdf2f2">Warm red tint</option>
        <option value="#d8d2c9">Beige</option>
        <option value="#9fad9f">Dark khaki</option>
        <option value="#f2dbdb">Light red</option>
        <option value="#b31b1b">Cornell red</option>
        <option value="#7a1216">Dark red</option>
        <option value="#073949">Navy blue</option>
        <option value="custom">Custom colour &rarr;</option>
      </select>
    </label>
    <label>Custom background<input type="color" id="bgcustom" value="#f7f7f7"></label>
    <label><input type="checkbox" id="backing" checked> Backing card behind captions &amp; author</label>
    <label><input type="checkbox" id="titleback" checked> Backing card behind the title</label>
  </fieldset>

  <fieldset>
    <legend>Sections</legend>
    <label><input type="checkbox" id="stats" checked> Stats band</label>
    <label><input type="checkbox" id="qr" checked> QR panel</label>
    <label><input type="checkbox" id="datasets" checked> Dataset thumbnails</label>
    <label><input type="checkbox" id="headshot" checked> Headshot</label>
    <label><input type="checkbox" id="authorqr" checked> QR beside author (timothyfraser.com)</label>
  </fieldset>

  <div id="fitmsg" class="ok">Checking fit…</div>
  <button onclick="window.print()">Print / Save as PDF</button>
  <button class="ghost" id="reset">Reset to defaults</button>
  <div class="hint">In the print dialog choose <b>Save as PDF</b>, paper size <b>40 × 30 in</b> (or "Custom"),
  margins <b>None</b>, and tick <b>Background graphics</b>.</div>
</div>

<div id="stage">
<div class="page">

  <header>
    <div>
      <h1>Production-Quality Interactive Course Labs, Built with AI</h1>
    </div>
    <div class="author">
      <img src="{HEAD}" alt="Tim Fraser">
      <div>
        <div class="name">Tim Fraser, Ph.D.</div>
        <div class="role">Assistant Teaching Professor, Systems Engineering</div>
        <div class="meta">Cornell University · tmf77@cornell.edu<br>SYSEN 5470 · timothyfraser.com/netsci</div>
      </div>
      <img class="author-qr" src="{QR_HOME}" alt="timothyfraser.com">
    </div>
  </header>

  <div class="stats">{stats_html}</div>

  <main>
    <div class="col">
      <div class="card">
        <h2>THE PROBLEM</h2>
        <p>{PROBLEM[0]}<span class="lvl2">{PROBLEM[1]}</span></p>
      </div>
      <div class="card">
        <h2>THE AI WORKFLOW</h2>
        <ol>{steps_html}</ol>
      </div>
      <div class="card" id="datacard">
        <h2>21 DATASETS</h2>
        <p>Each hides a planted story, with R + Python loaders.<span class="lvl2"> Codebooks included.</span></p>
        <div class="stamps">{stamps_html}</div>
      </div>
    </div>

    <div class="col">
      <figure>
        <img id="fig-lab" alt="Interactive case-study lab">
        <figcaption>{cap('lab')}</figcaption>
      </figure>
      <figure>
        <img id="fig-pg" alt="Coding playground running a network plot">
        <figcaption>{cap('pg')}</figcaption>
      </figure>
    </div>

    <div class="col">
      <figure>
        <img id="fig-viz" alt="Network visualizer">
        <figcaption>{cap('viz')}</figcaption>
      </figure>
      <div class="card">
        <h2>WHAT STUDENTS GET</h2>
        <ul>{gets_html}</ul>
      </div>
      <div class="card" id="qrcard">
        <h2>TRY IT RIGHT NOW</h2>
        <div class="qr">
          <div><img src="{QR_SITE}" alt=""><span>Course site</span></div>
          <div><img src="{QR_VIZ}" alt=""><span>Network Visualizer</span></div>
        </div>
      </div>
    </div>
  </main>

</div>
</div>

<script>
const FIGS = {figs_js};
const root = document.documentElement.style, body = document.body;

function setTheme(t) {{
  document.getElementById('fig-lab').src = FIGS[t].lab;
  document.getElementById('fig-viz').src = FIGS[t].viz;
  document.getElementById('fig-pg').src  = FIGS[t].pg;
}}
document.querySelectorAll('input[name=theme]').forEach(r =>
  r.addEventListener('change', e => setTheme(e.target.value)));
document.querySelectorAll('input[name=detail]').forEach(r =>
  r.addEventListener('change', e => body.dataset.detail = e.target.value));

const bind = (id, fn) => document.getElementById(id).addEventListener('input', fn);
bind('fs', e => {{ root.setProperty('--fs', e.target.value / 100); document.getElementById('fsv').textContent = e.target.value + '%'; }});
bind('ts', e => {{ root.setProperty('--ts', e.target.value / 100); document.getElementById('tsv').textContent = e.target.value + '%'; }});
bind('zoom', e => {{ root.setProperty('--zoom', e.target.value / 100); document.getElementById('zv').textContent = e.target.value + '%'; }});
bind('accent', e => root.setProperty('--accent', e.target.value));
// ---- the three colour roles -------------------------------------------------
const $ = (id) => document.getElementById(id);

function lum(hex) {{
  const m = /^#([0-9a-f]{{6}})$/i.exec((hex || '').trim());
  if (!m) return 1;
  const n = parseInt(m[1], 16);
  return (0.2126 * ((n >> 16) & 255) + 0.7152 * ((n >> 8) & 255) + 0.0722 * (n & 255)) / 255;
}}
const rgba = (hex, a) => {{
  const m = /^#([0-9a-f]{{6}})$/i.exec(hex || '');
  if (!m) return hex;
  const n = parseInt(m[1], 16);
  return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
}};

function applyCard(hex) {{
  const dark = lum(hex) < 0.45;
  root.setProperty('--card-bg', hex);
  root.setProperty('--card-ink', dark ? '#ffffff' : '#1c1c1c');
  root.setProperty('--card-body', dark ? '#f6ecec' : '#333333');
  root.setProperty('--card-h2', dark ? '#F7C948' : $('accent').value);
  root.setProperty('--card-line', dark ? 'rgba(255,255,255,.30)' : 'rgba(0,0,0,.12)');
  root.setProperty('--card-shadow', dark ? '0 3px 12px rgba(0,0,0,.30)' : '0 3px 12px rgba(0,0,0,.10)');
  root.setProperty('--backing', rgba(hex, 0.92));
  $('cardcol').value = hex;
  applyTitle();
}}
function applyBg(val) {{
  if (val === 'template') {{
    body.dataset.bg = 'template';
    root.setProperty('--page-ink', '#1c1c1c');
  }} else {{
    const colour = (val === 'custom') ? $('bgcustom').value : val;
    body.dataset.bg = 'color';
    root.setProperty('--page-color', colour);
    root.setProperty('--page-ink', lum(colour) < 0.45 ? '#ffffff' : '#1c1c1c');
  }}
  applyTitle();
}}
function applyTitle() {{
  // the title sits either on its backing card or straight on the page
  const onCard = body.dataset.titleback === 'on';
  const base = onCard ? $('cardcol').value
             : (body.dataset.bg === 'template' ? '#ffffff'
                : (($('bg').value === 'custom') ? $('bgcustom').value : $('bg').value));
  root.setProperty('--title-color', lum(base) < 0.45 ? '#F7C948' : $('accent').value);
}}

$('bg').addEventListener('change', e => applyBg(e.target.value));
$('bgcustom').addEventListener('input', () => {{ $('bg').value = 'custom'; applyBg('custom'); }});
$('cardcol').addEventListener('input', e => applyCard(e.target.value));
$('nocards').addEventListener('change', e => body.dataset.cards = e.target.checked ? 'none' : 'solid');
['backing','titleback'].forEach(id =>
  $(id).addEventListener('change', e => {{
    body.dataset[id] = e.target.checked ? 'on' : 'off';
    applyTitle();
  }}));

// card-colour swatches
const CARD_SWATCHES = ['#ffffff', '#f7f7f7', '#f9e4e4', '#f2dbdb', '#b31b1b', '#8c1515'];
CARD_SWATCHES.forEach(c => {{
  const sp = document.createElement('span');
  sp.style.background = c;
  sp.title = c;
  sp.addEventListener('click', () => applyCard(c));
  $('cardsw').appendChild(sp);
}});

// ---- one-click combinations -------------------------------------------------
const COMBOS = {{
  default:  {{ theme: 'red',      card: '#ffffff', bg: 'template' }},
  a:        {{ theme: 'reddark',  card: '#f9e4e4', bg: '#f7f7f7' }},
  b:        {{ theme: 'white',    card: '#f9e4e4', bg: '#b31b1b' }},
  c:        {{ theme: 'redlight', card: '#ffffff', bg: '#7a1216' }},
  d:        {{ theme: 'redlight', card: '#8c1515', bg: '#ffffff' }},
}};
document.querySelectorAll('button.combo').forEach(btn =>
  btn.addEventListener('click', () => {{
    const c = COMBOS[btn.dataset.combo];
    setTheme(c.theme);
    const r = document.querySelector('input[name=theme][value="' + c.theme + '"]');
    if (r) r.checked = true;
    applyCard(c.card);
    $('bg').value = c.bg;
    applyBg(c.bg);
    setTimeout(checkFit, 80);
  }}));
['stats','qr','datasets','headshot','authorqr'].forEach(id =>
  document.getElementById(id).addEventListener('change', e => body.dataset[id] = e.target.checked ? 'on' : 'off'));

document.getElementById('reset').addEventListener('click', () => location.reload());

function checkFit() {{
  const cols = [...document.querySelectorAll('main > .col')];
  const over = cols.map((c, i) => (c.scrollHeight - c.clientHeight > 3 ? i + 1 : 0)).filter(Boolean);
  const el = document.getElementById('fitmsg');
  if (over.length) {{
    el.textContent = '\u26a0 Column ' + over.join(' & ') + ' overflows the page — reduce text size, detail level, or figure size.';
    el.className = 'warn';
  }} else {{
    el.textContent = '\u2713 Everything fits on one 40 \u00d7 30 in page.';
    el.className = 'ok';
  }}
}}
document.querySelectorAll('#sidebar input, #sidebar select').forEach(el =>
  el.addEventListener('input', () => setTimeout(checkFit, 60)));
window.addEventListener('load', () => setTimeout(checkFit, 400));


// fit the poster to the window on first paint
(function fit() {{
  const avail = window.innerWidth - 330 - 60;
  const z = Math.max(0.10, Math.min(0.60, avail / (40 * 96)));
  root.setProperty('--zoom', z);
  const s = document.getElementById('zoom');
  s.value = Math.round(z * 100);
  document.getElementById('zv').textContent = Math.round(z * 100) + '%';
}})();

// ?theme=white&detail=2&ts=100&fs=100&print=1  — used to render fixed variants headlessly
(function fromUrl() {{
  const q = new URLSearchParams(location.search);
  const t = q.get('theme') || 'red';
  setTheme(t);
  const r = document.querySelector('input[name=theme][value="' + t + '"]');
  if (r) r.checked = true;
  const d = q.get('detail') || '1';
  body.dataset.detail = d;
  const rd = document.querySelector('input[name=detail][value="' + d + '"]');
  if (rd) rd.checked = true;
  root.setProperty('--ts', (+q.get('ts') || 110) / 100);
  root.setProperty('--fs', (+q.get('fs') || 110) / 100);
  document.getElementById('ts').value = +q.get('ts') || 110;
  document.getElementById('fs').value = +q.get('fs') || 110;
  document.getElementById('tsv').textContent = (+q.get('ts') || 110) + '%';
  document.getElementById('fsv').textContent = (+q.get('fs') || 110) + '%';
  const combo = q.get('combo');
  if (combo && COMBOS[combo]) {{
    const c = COMBOS[combo];
    setTheme(c.theme);
    const rr = document.querySelector('input[name=theme][value="' + c.theme + '"]');
    if (rr) rr.checked = true;
    applyCard(c.card); $('bg').value = c.bg; applyBg(c.bg);
  }} else {{
    applyCard(q.get('card') || '#ffffff');
    const bgv = q.get('bg') || 'template';
    $('bg').value = bgv; applyBg(bgv);
  }}
}})();
</script>
</body>
</html>
"""

OUT.write_text(HTML, encoding="utf-8")
print(f"\nwrote {OUT}  ({OUT.stat().st_size/1024/1024:.1f} MB)")
