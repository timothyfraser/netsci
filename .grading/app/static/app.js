(function () {
  var state = {
    rows: [],
    rubric: null,
    assignments: [],
    activeKey: null,
    detail: null,
    issueFilter: "",
    loading: {
      classbot: false,
      batch: false,
      sync: false,
      save: false,
      publish: false,
      detail: false,
    },
    loadingMessage: "",
    loadingMessages: {},
    batchTotal: 0,
    batchDone: 0,
  };

  var els = {
    queue: document.getElementById("queue-list"),
    queuePanel: document.querySelector(".queue-panel"),
    detail: document.getElementById("detail-panel"),
    globalStatus: document.getElementById("global-status"),
    globalStatusText: document.getElementById("global-status-text"),
    batchStatus: document.getElementById("batch-status"),
    batchStatusText: document.getElementById("batch-status-text"),
    filterAssignment: document.getElementById("filter-assignment"),
    filterStatus: document.getElementById("filter-status"),
    filterReport: document.getElementById("filter-report"),
    modelSelect: document.getElementById("model-select"),
    btnSync: document.getElementById("btn-sync"),
    btnSeed: document.getElementById("btn-seed"),
    btnBatch: document.getElementById("btn-batch-classbot"),
    modal: document.getElementById("modal"),
    modalPreview: document.getElementById("modal-preview"),
    modalCancel: document.getElementById("modal-cancel"),
    modalConfirm: document.getElementById("modal-confirm"),
  };

  function isLoading() {
    return Object.keys(state.loading).some(function (k) { return state.loading[k]; });
  }

  var LOADING_MSG_ORDER = ["publish", "classbot", "batch", "sync", "save", "detail"];

  function refreshLoadingMessage() {
    for (var i = 0; i < LOADING_MSG_ORDER.length; i++) {
      var k = LOADING_MSG_ORDER[i];
      if (state.loading[k] && state.loadingMessages[k]) {
        state.loadingMessage = state.loadingMessages[k];
        return;
      }
    }
    state.loadingMessage = "";
  }

  function setLoading(key, on, message) {
    state.loading[key] = !!on;
    if (on && message) state.loadingMessages[key] = message;
    if (!on) state.loadingMessages[key] = "";
    refreshLoadingMessage();
    updateLoadingUI();
  }

  function setLoadingMessage(key, message) {
    state.loadingMessages[key] = message;
    refreshLoadingMessage();
    if (els.globalStatusText && state.loadingMessage) {
      els.globalStatusText.textContent = state.loadingMessage;
    }
    updateBatchProgressUI();
  }

  function batchProgressCounts() {
    var total = state.batchTotal || 0;
    if (state.loading.batch && total) {
      var done = state.batchDone || 0;
      return { total: total, done: done, remaining: Math.max(0, total - done) };
    }
    var remaining = pendingForAssignment().length;
    var done = total ? Math.max(0, total - remaining) : 0;
    return { total: total, done: done, remaining: remaining };
  }

  function updateBatchProgressUI() {
    if (els.queuePanel) {
      els.queuePanel.classList.toggle("is-busy", state.loading.batch);
    }
    if (!els.batchStatus) return;
    if (state.loading.batch) {
      els.batchStatus.classList.remove("hidden");
      var p = batchProgressCounts();
      if (els.batchStatusText) {
        els.batchStatusText.textContent = p.total
          ? "Classbot running — " + p.done + " of " + p.total + " complete. Queue refreshes as rows finish."
          : (state.loadingMessages.batch || "Classbot batch running…");
      }
    } else if (state.loading.classbot) {
      els.batchStatus.classList.remove("hidden");
      if (els.batchStatusText) {
        els.batchStatusText.textContent = state.loadingMessages.classbot || "Classbot reviewing this submission…";
      }
    } else {
      els.batchStatus.classList.add("hidden");
    }
  }

  function refreshAfterClassbot() {
    var key = state.activeKey;
    return loadRows().then(function () {
      if (key) return selectRow(key, { force: true });
    });
  }

  function runClassbotOneKey(key, model) {
    return api("/api/classbot/" + encodeURIComponent(key), {
      method: "POST",
      body: { model: model, mode: "text" },
    });
  }

  /** Run Classbot on many keys with bounded parallelism; updates progress after each. */
  function runClassbotPool(keys, model, concurrency) {
    concurrency = concurrency || 5;
    return new Promise(function (resolve) {
      if (!keys.length) {
        resolve({ errors: [], total: 0 });
        return;
      }
      var index = 0;
      var active = 0;
      var finished = 0;
      var errors = [];
      var total = keys.length;
      var settled = false;

      function pump() {
        while (active < concurrency && index < keys.length) {
          (function (key) {
            active++;
            runClassbotOneKey(key, model)
              .catch(function (err) {
                errors.push({ key: key, error: err.message || String(err) });
              })
              .finally(function () {
                active--;
                finished++;
                state.batchDone = finished;
                setLoadingMessage(
                  "batch",
                  "Classbot batch (" + finished + "/" + total + ")…"
                );
                updateLoadingUI();
                loadRows();
                pump();
                if (finished >= total && !settled) {
                  settled = true;
                  resolve({ errors: errors, total: total });
                }
              });
          })(keys[index]);
          index++;
        }
      }

      pump();
    });
  }

  function rowNeedsClassbot(row) {
    if (!row.cached_text_path) return false;
    if (row.llm_status === "pending") return true;
    if (!row.llm_review_path) return true;
    if (row.llm_status === "error") return true;
    return false;
  }

  function pendingForAssignment() {
    var key = els.filterAssignment.value;
    if (!key) return [];
    return state.rows.filter(rowNeedsClassbot);
  }

  function updateBatchButton() {
    if (!els.btnBatch || state.loading.batch) return;
    var assignment = els.filterAssignment.value;
    if (!assignment) {
      els.btnBatch.textContent = "Run Classbot (pick assignment)";
      els.btnBatch.disabled = state.loading.classbot;
      els.btnBatch.title = "Select an assignment in the filter above to batch-run Classbot.";
      return;
    }
    var n = pendingForAssignment().length;
    els.btnBatch.textContent = n
      ? "Run Classbot (" + n + " pending)"
      : "Run Classbot (none pending)";
    els.btnBatch.disabled = state.loading.classbot || !n;
    els.btnBatch.title = n
      ? "Run Classbot in parallel for all pending submissions with text in this assignment."
      : "No pending submissions with text for this assignment.";
  }

  function updateLoadingUI() {
    if (els.globalStatus) {
      els.globalStatus.classList.toggle("hidden", !isLoading());
    }
    if (els.globalStatusText && state.loadingMessage) {
      els.globalStatusText.textContent = state.loadingMessage;
    } else if (els.globalStatusText) {
      els.globalStatusText.textContent = "Working…";
    }
    if (els.btnSync) els.btnSync.disabled = state.loading.sync;
    if (els.btnBatch) {
      els.btnBatch.disabled = state.loading.batch || state.loading.classbot;
      els.btnBatch.classList.toggle("is-running", state.loading.batch || state.loading.classbot);
      if (state.loading.batch) {
        var bp = batchProgressCounts();
        var batchLabel = bp.total
          ? "Running " + bp.done + "/" + bp.total + "…"
          : "Running…";
        els.btnBatch.innerHTML =
          "<span class='spinner' aria-hidden='true'></span> " + batchLabel;
      } else if (state.loading.classbot) {
        els.btnBatch.innerHTML = "<span class='spinner' aria-hidden='true'></span> Running…";
      } else {
        updateBatchButton();
      }
    }

    var btnClassbot = document.getElementById("btn-classbot");
    if (btnClassbot) {
      btnClassbot.disabled = state.loading.classbot || state.loading.batch;
      if (state.loading.classbot) {
        btnClassbot.innerHTML = "<span class='spinner' aria-hidden='true'></span> Classbot running…";
      } else {
        btnClassbot.textContent = "Re-run Classbot";
      }
    }
    var btnSave = document.getElementById("btn-save");
    if (btnSave) btnSave.disabled = state.loading.save || state.loading.classbot || state.loading.publish;
    var btnPublish = document.getElementById("btn-publish");
    if (btnPublish) btnPublish.disabled = state.loading.publish || state.loading.classbot || state.loading.save;
    if (els.modalConfirm) els.modalConfirm.disabled = state.loading.publish;
    updateBatchProgressUI();
  }

  function api(path, opts) {
    opts = opts || {};
    return fetch(path, {
      method: opts.method || "GET",
      headers: opts.body ? { "Content-Type": "application/json" } : {},
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }).then(function (r) {
      if (!r.ok) {
        return r.json().then(function (j) {
          throw new Error(j.detail || r.statusText);
        }).catch(function () {
          throw new Error(r.statusText);
        });
      }
      return r.json();
    });
  }

  function loadConfig() {
    return api("/api/config").then(function (cfg) {
      state.rubric = cfg.rubric;
      state.assignments = cfg.assignments;
      cfg.assignments.forEach(function (a) {
        var opt = document.createElement("option");
        opt.value = a.key;
        opt.textContent = a.name;
        els.filterAssignment.appendChild(opt);
      });
    });
  }

  function loadRows() {
    var q = [];
    if (els.filterAssignment.value) q.push("assignment_key=" + encodeURIComponent(els.filterAssignment.value));
    if (els.filterStatus.value) q.push("status=" + encodeURIComponent(els.filterStatus.value));
    if (els.filterReport.value === "yes") q.push("has_report=true");
    if (els.filterReport.value === "no") q.push("has_report=false");
    var url = "/api/rows" + (q.length ? "?" + q.join("&") : "");
    return api(url).then(function (rows) {
      state.rows = rows;
      renderQueue();
    });
  }

  function renderQueue() {
    els.queue.innerHTML = "";
    if (!state.rows.length) {
      els.queue.innerHTML = "<p class='placeholder'>No rows. Sync Canvas or seed demo.</p>";
      updateBatchButton();
      return;
    }
    state.rows.forEach(function (row) {
      var div = document.createElement("div");
      div.className = "queue-item" + (row.submission_key === state.activeKey ? " active" : "");
      var score = row.final_grade || row.proposed_score || "—";
      div.innerHTML =
        "<div class='name'>" + esc(displayName(row)) + "</div>" +
        "<div class='meta'>" +
        "<span class='badge'>" + esc(row.assignment_key) + "</span>" +
        "<span class='badge'>" + esc(row.status || "synced") + "</span>" +
        (row.late === "true" ? "<span class='badge'>late</span>" : "") +
        (!row.cached_text_path ? "<span class='badge warn'>no text</span>" : "") +
        "<br>" + esc(row.student_netid) + " · score " + esc(String(score)) +
        "</div>";
      div.addEventListener("click", function () {
        selectRow(row.submission_key);
      });
      els.queue.appendChild(div);
    });
    updateBatchButton();
  }

  function selectRow(key, options) {
    options = options || {};
    if (!options.force && (state.loading.classbot || state.loading.batch)) return;
    state.activeKey = key;
    renderQueue();
    setLoading("detail", true, "Loading submission…");
    els.detail.innerHTML =
      "<div class='detail-loading'><span class='spinner' aria-hidden='true'></span> Loading submission…</div>";
    api("/api/rows/" + encodeURIComponent(key))
      .then(function (data) {
        state.detail = data;
        renderDetail();
      })
      .catch(function (err) {
        els.detail.innerHTML = "<p class='placeholder'>Failed to load row.</p>";
        alertError(err);
      })
      .finally(function () { setLoading("detail", false); });
  }

  function displayName(row) {
    if (row.student_display_name) return row.student_display_name;
    var raw = row.student_name || "";
    if (raw.indexOf(",") !== -1) {
      var parts = raw.split(",");
      return parts[1].trim() + " " + parts[0].trim();
    }
    return raw || "Unknown";
  }

  function instructorCommentSection(body) {
    return (
      section(
        "Instructor comment",
        "<div class='emoji-toolbar' aria-label='Insert emoji'>" +
        "<button type='button' class='emoji-btn' data-emoji='👍' title='Thumbs up'>👍</button>" +
        "<button type='button' class='emoji-btn' data-emoji='😊' title='Smile'>😊</button>" +
        "<button type='button' class='emoji-btn' data-emoji='❓' title='Question'>❓</button>" +
        "<button type='button' class='emoji-btn' data-emoji='✅' title='Checkmark'>✅</button>" +
        "<button type='button' class='emoji-btn' data-emoji='❌' title='Red X'>❌</button>" +
        "</div>" +
        "<textarea id='instructor-comment'>" + esc(body || "") + "</textarea>",
        false
      )
    );
  }

  function insertAtCursor(textarea, text) {
    if (!textarea) return;
    var start = textarea.selectionStart;
    var end = textarea.selectionEnd;
    var val = textarea.value || "";
    textarea.value = val.slice(0, start) + text + val.slice(end);
    var pos = start + text.length;
    textarea.selectionStart = pos;
    textarea.selectionEnd = pos;
    textarea.focus();
  }

  function wireEmojiToolbar() {
    document.querySelectorAll(".emoji-btn").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var ta = document.getElementById("instructor-comment");
        insertAtCursor(ta, btn.getAttribute("data-emoji") || "");
      });
    });
  }

  function rubricLabel(id) {
    if (!state.rubric) return id;
    var req = state.rubric.requirements.find(function (r) { return r.id === id; });
    return req ? req.label : id;
  }

  function section(title, bodyHtml, open) {
    return (
      "<details class='section'" + (open ? " open" : "") + ">" +
      "<summary><h3>" + title + "</h3></summary>" +
      "<div class='section-body'>" + bodyHtml + "</div>" +
      "</details>"
    );
  }

  function updateClassbotPreview() {
    var ta = document.getElementById("classbot-comment");
    var prev = document.getElementById("classbot-preview");
    if (!ta || !prev) return;
    var raw = ta.value || "";
    if (raw.trim().startsWith("<")) {
      prev.innerHTML = raw;
    } else {
      prev.textContent = raw || "(empty)";
    }
  }

  function assignmentMeta(key) {
    for (var i = 0; i < state.assignments.length; i++) {
      if (state.assignments[i].key === key) return state.assignments[i];
    }
    return null;
  }

  function isLearningChecks(row) {
    return (row.assignment_type === "learning_checks") ||
      (state.detail && state.detail.assignment_type === "learning_checks");
  }

  function renderLcChecks(review) {
    if (!review || !review.checks) return "<p class='placeholder'>Run Classbot to verify LC answers.</p>";
    var html = "<div class='lc-checks'>";
    review.checks.forEach(function (chk) {
      var emoji = { correct: "✅", incorrect: "❌", missing: "📭", unclear: "❓" }[chk.verdict] || "•";
      html +=
        "<div class='issue-card'>" +
        "<strong>" + emoji + " " + esc(chk.label || chk.id) + "</strong>" +
        "<div>Submitted: <em>" + esc(chk.student_answer || "—") + "</em> · Key: <em>" + esc(chk.correct_answer || "—") + "</em></div>" +
        "<div>" + esc(chk.feedback || "") + "</div></div>";
    });
    if (review.code_answer) {
      var ca = review.code_answer;
      var cemoji = { correct: "✅", incorrect: "❌", missing: "📭", unclear: "❓" }[ca.verdict] || "•";
      html +=
        "<div class='issue-card'>" +
        "<strong>" + cemoji + " ⌨️ I ran the code</strong>" +
        "<div>Student: <em>" + esc(ca.student_value || "—") + "</em></div>" +
        "<div>" + esc(ca.feedback || "") + "</div></div>";
    }
    html += "</div>";
    return html;
  }

  function renderDetail() {
    if (!state.detail) return;
    var row = state.detail.row;
    var review = state.detail.review;
    var deductions = state.detail.deductions || [];
    var dedMap = {};
    deductions.forEach(function (d) { dedMap[d.id] = d; });
    var lc = isLearningChecks(row);
    var pointsMax = state.detail.points_max || (lc ? 1 : 100);
    var defaultGrade = row.final_grade || row.proposed_score || (lc ? "1" : "100");

    var middleSections = "";
    if (lc) {
      middleSections =
        section("Learning check review", renderLcChecks(review), true) +
        (review && review.classbot_summary
          ? section("Classbot summary", "<p>" + esc(review.classbot_summary) + "</p>", false)
          : "");
    } else {
      var reqsHtml = "";
      var sourceReqs = review && review.requirements ? review.requirements : [];
      if (!sourceReqs.length && state.rubric) {
        sourceReqs = state.rubric.requirements.map(function (r) {
          return { id: r.id, status: "not_assessable", evidence: "Run Classbot", location: "", proposed_deduction: 0 };
        });
      }
      sourceReqs.forEach(function (req) {
        var d = dedMap[req.id] || {};
        var accepted = d.accepted !== undefined ? d.accepted : (req.status === "partial" || req.status === "missing");
        var ded = d.deduction !== undefined ? d.deduction : (req.proposed_deduction || 0);
        reqsHtml +=
          "<div class='req-row' data-req-id='" + esc(req.id) + "'>" +
          "<input type='checkbox' class='req-accept' " + (accepted ? "checked" : "") + ">" +
          "<div>" +
          "<div class='req-label'>" + esc(rubricLabel(req.id)) +
          " <span class='status-chip status-" + esc(req.status || "missing") + "'>" + esc(req.status || "") + "</span></div>" +
          "<div class='req-evidence'>" + esc(req.evidence || d.evidence || "") + "</div>" +
          "<div class='req-loc'>" + esc(req.location || d.location || "") +
          (req.search_hint || d.search_hint ? " · [" + esc(req.search_hint || d.search_hint) + "]" : "") +
          "</div></div>" +
          "<input type='number' class='deduction-input' min='0' max='100' value='" + esc(String(ded)) + "'>" +
          "</div>";
      });

      var issuesHtml = "";
      var issues = (review && review.top_issues) || [];
      issues.forEach(function (issue) {
        if (state.issueFilter) {
          var hay = (issue.title + " " + issue.description + " " + issue.location + " " + issue.search_hint).toLowerCase();
          if (hay.indexOf(state.issueFilter.toLowerCase()) === -1) return;
        }
        issuesHtml +=
          "<div class='issue-card'>" +
          "<strong>#" + esc(String(issue.rank)) + " " + esc(issue.title) + "</strong>" +
          "<div>" + esc(issue.description || "") + "</div>" +
          "<div class='req-loc'>" + esc(issue.location || "") + "</div>" +
          "<div class='hint'>" + esc(issue.search_hint || "") + "</div></div>";
      });
      if (!issuesHtml) issuesHtml = "<p class='placeholder'>No issues yet.</p>";

      middleSections =
        section("Requirements", reqsHtml, true) +
        section("Top issues", "<input type='text' class='search-box' id='issue-search' placeholder='Search issues…' value='" + esc(state.issueFilter) + "'>" + issuesHtml, true);
    }

    var previewLabel = lc ? "Submission text" : "Report preview";
    els.detail.innerHTML =
      "<div class='meta-bar'>" +
      "<span>" + esc(displayName(row)) + " (" + esc(row.student_netid) + ")</span>" +
      "<span>" + esc(row.assignment_name) + "</span>" +
      (lc ? "<span>📚 LC</span>" : "") +
      "<span>Attempt " + esc(row.attempt_number) + "</span>" +
      (row.late === "true" ? "<span>LATE</span>" : "") +
      "<span>Status: " + esc(row.status) + "</span>" +
      "</div>" +

      "<div class='score-row'>" +
      "<label>Final grade</label>" +
      "<input type='number' id='final-grade' min='0' max='" + esc(String(pointsMax)) + "' value='" + esc(String(defaultGrade)) + "'>" +
      "<span class='feedback' id='save-feedback'></span>" +
      "</div>" +

      section(previewLabel, "<div class='report-preview' id='report-preview'>Loading…</div>", true) +
      middleSections +
      instructorCommentSection(row.instructor_comment) +
      section(
        "Classbot comment",
        "<p class='placeholder' style='margin:12px 0 6px;font-size:11px;'>HTML stored here — preview below is what Canvas will render.</p>" +
        "<textarea id='classbot-comment' rows='8'>" + esc(row.classbot_comment || "") + "</textarea>" +
        "<div id='classbot-preview' class='classbot-preview'></div>",
        true
      ) +

      "<div class='actions-row'>" +
      "<button class='btn' id='btn-save'>Save</button>" +
      "<button class='btn ghost' id='btn-classbot'>Re-run Classbot</button>" +
      "<button class='btn' id='btn-publish'>Publish to Canvas</button>" +
      "</div>";

    api("/api/report-text/" + encodeURIComponent(row.submission_key)).then(function (r) {
      var el = document.getElementById("report-preview");
      if (el) el.textContent = r.text || "(no cached text)";
    });

    var issueSearch = document.getElementById("issue-search");
    if (issueSearch) {
      issueSearch.addEventListener("input", function (e) {
        state.issueFilter = e.target.value;
        renderDetail();
      });
    }

    wireEmojiToolbar();

    var cb = document.getElementById("classbot-comment");
    if (cb) {
      cb.addEventListener("input", updateClassbotPreview);
      updateClassbotPreview();
    }

    document.getElementById("btn-save").addEventListener("click", saveCurrent);
    document.getElementById("btn-classbot").addEventListener("click", runClassbot);
    document.getElementById("btn-publish").addEventListener("click", openPublishModal);
    updateLoadingUI();
  }

  function collectDeductions() {
    var out = [];
    document.querySelectorAll(".req-row").forEach(function (row) {
      var id = row.getAttribute("data-req-id");
      var accepted = row.querySelector(".req-accept").checked;
      var ded = parseInt(row.querySelector(".deduction-input").value, 10) || 0;
      out.push({ id: id, accepted: accepted, deduction: ded, proposed_deduction: ded });
    });
    return out;
  }

  function saveCurrent() {
    if (!state.activeKey || state.loading.save || state.loading.classbot) return Promise.resolve();
    setLoading("save", true, "Saving…");
    var body = {
      accepted_deductions_json: JSON.stringify(collectDeductions()),
      final_grade: document.getElementById("final-grade").value,
      instructor_comment: document.getElementById("instructor-comment").value,
      classbot_comment: document.getElementById("classbot-comment").value,
      status: "reviewed",
    };
    return api("/api/rows/" + encodeURIComponent(state.activeKey), { method: "PATCH", body: body })
      .then(function () {
        var fb = document.getElementById("save-feedback");
        if (fb) { fb.textContent = "Saved."; setTimeout(function () { fb.textContent = ""; }, 2500); }
        return loadRows().then(function () { selectRow(state.activeKey); });
      })
      .catch(alertError)
      .finally(function () { setLoading("save", false); });
  }

  function runClassbot() {
    if (!state.activeKey || state.loading.classbot) return;
    var model = els.modelSelect.value;
    setLoading("classbot", true, "Classbot reviewing…");
    runClassbotOneKey(state.activeKey, model)
      .then(function () {
        setLoading("classbot", false);
        return refreshAfterClassbot();
      })
      .catch(alertError)
      .finally(function () { setLoading("classbot", false); });
  }

  function openPublishModal() {
    if (!state.detail) return;
    var grade = document.getElementById("final-grade").value;
    var instructor = document.getElementById("instructor-comment").value;
    var classbot = document.getElementById("classbot-comment").value;
    api("/api/compose-preview", {
      method: "POST",
      body: {
        instructor_comment: instructor,
        classbot_comment: classbot,
        assignment_key: state.detail.row.assignment_key,
      },
    }).then(function (resp) {
      els.modalPreview.innerHTML =
        "<p><strong>Grade: " + esc(grade) + "</strong></p>" +
        "<div class='preview-html'>" + resp.html + "</div>";
      els.modal.classList.remove("hidden");
    }).catch(alertError);
  }

  els.modalCancel.addEventListener("click", function () {
    els.modal.classList.add("hidden");
  });

  els.modalConfirm.addEventListener("click", function () {
    if (!state.activeKey || state.loading.publish) return;
    var grade = document.getElementById("final-grade").value;
    setLoading("publish", true, "Publishing to Canvas…");
    saveCurrent().then(function () {
      return api("/api/publish/" + encodeURIComponent(state.activeKey), {
        method: "POST",
        body: { final_grade: grade },
      });
    }).then(function () {
      els.modal.classList.add("hidden");
      return loadRows().then(function () { selectRow(state.activeKey); });
    }).catch(alertError)
      .finally(function () { setLoading("publish", false); });
  });

  els.btnSync.addEventListener("click", function () {
    if (state.loading.sync) return;
    var key = els.filterAssignment.value;
    setLoading("sync", true, "Syncing from Canvas…");
    var path = key ? "/api/sync" : "/api/sync-all";
    var body = key ? { assignment_key: key, force: true } : { force: true };
    api(path, { method: "POST", body: body })
      .then(function () { return loadRows(); })
      .catch(alertError)
      .finally(function () { setLoading("sync", false); });
  });

  els.btnSeed.addEventListener("click", function () {
    api("/api/seed-demo", { method: "POST" })
      .then(function () { return loadRows(); })
      .catch(alertError);
  });

  els.btnBatch.addEventListener("click", function () {
    if (state.loading.batch || state.loading.classbot) return;
    var assignmentKey = els.filterAssignment.value;
    if (!assignmentKey) {
      alert("Select an assignment in the filter above first.");
      return;
    }
    var pending = pendingForAssignment();
    if (!pending.length) {
      alert("No pending submissions with text for this assignment.");
      return;
    }
    var label = state.assignments.find(function (a) { return a.key === assignmentKey; });
    var name = label ? label.name : assignmentKey;
    if (!confirm(
      "Run Classbot on " + pending.length + " pending submission(s) for “" + name + "”?\n\n" +
      "Skips rows with no text. Runs up to 5 LLM requests in parallel."
    )) {
      return;
    }
    var keys = pending.map(function (r) { return r.submission_key; });
    state.batchTotal = keys.length;
    state.batchDone = 0;
    setLoading("batch", true, "Classbot batch (0/" + keys.length + ")…");

    setTimeout(function () {
      runClassbotPool(keys, els.modelSelect.value, 5)
        .then(function (result) {
          if (result.errors.length) {
            alert(
              "Classbot finished: " + (result.total - result.errors.length) +
              " ok, " + result.errors.length + " failed."
            );
          }
        })
        .catch(alertError)
        .finally(function () {
          state.batchTotal = 0;
          state.batchDone = 0;
          setLoading("batch", false);
        })
        .then(function () {
          return refreshAfterClassbot();
        });
    }, 0);
  });

  els.filterAssignment.addEventListener("change", loadRows);
  els.filterStatus.addEventListener("change", loadRows);
  els.filterReport.addEventListener("change", loadRows);

  function esc(s) {
    return String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  }

  function alertError(err) {
    alert(err.message || String(err));
  }

  loadConfig().then(loadRows);
})();
