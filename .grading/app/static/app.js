(function () {
  var state = {
    rows: [],
    rubric: null,
    assignments: [],
    activeKey: null,
    detail: null,
    issueFilter: "",
  };

  var els = {
    queue: document.getElementById("queue-list"),
    detail: document.getElementById("detail-panel"),
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
      return;
    }
    state.rows.forEach(function (row) {
      var div = document.createElement("div");
      div.className = "queue-item" + (row.submission_key === state.activeKey ? " active" : "");
      var score = row.final_grade || row.proposed_score || "—";
      div.innerHTML =
        "<div class='name'>" + esc(row.student_name || "Unknown") + "</div>" +
        "<div class='meta'>" +
        "<span class='badge'>" + esc(row.assignment_key) + "</span>" +
        "<span class='badge'>" + esc(row.status || "synced") + "</span>" +
        (row.late === "true" ? "<span class='badge'>late</span>" : "") +
        (!row.cached_text_path ? "<span class='badge warn'>no report</span>" : "") +
        "<br>" + esc(row.student_netid) + " · score " + esc(String(score)) +
        "</div>";
      div.addEventListener("click", function () {
        selectRow(row.submission_key);
      });
      els.queue.appendChild(div);
    });
  }

  function selectRow(key) {
    state.activeKey = key;
    renderQueue();
    api("/api/rows/" + encodeURIComponent(key)).then(function (data) {
      state.detail = data;
      renderDetail();
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

  function renderDetail() {
    if (!state.detail) return;
    var row = state.detail.row;
    var review = state.detail.review;
    var deductions = state.detail.deductions || [];
    var dedMap = {};
    deductions.forEach(function (d) { dedMap[d.id] = d; });

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

    els.detail.innerHTML =
      "<div class='meta-bar'>" +
      "<span>" + esc(row.student_name) + " (" + esc(row.student_netid) + ")</span>" +
      "<span>" + esc(row.assignment_name) + "</span>" +
      "<span>Attempt " + esc(row.attempt_number) + "</span>" +
      (row.late === "true" ? "<span>LATE</span>" : "") +
      "<span>Status: " + esc(row.status) + "</span>" +
      "</div>" +

      "<div class='score-row'>" +
      "<label>Final grade</label>" +
      "<input type='number' id='final-grade' min='0' max='100' value='" + esc(row.final_grade || row.proposed_score || "100") + "'>" +
      "<span class='feedback' id='save-feedback'></span>" +
      "</div>" +

      section("Report preview", "<div class='report-preview' id='report-preview'>Loading…</div>", true) +
      section("Requirements", reqsHtml, true) +
      section("Top issues", "<input type='text' class='search-box' id='issue-search' placeholder='Search issues…' value='" + esc(state.issueFilter) + "'>" + issuesHtml, true) +
      section("Instructor comment", "<textarea id='instructor-comment'>" + esc(row.instructor_comment || "") + "</textarea>", false) +
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

    document.getElementById("issue-search").addEventListener("input", function (e) {
      state.issueFilter = e.target.value;
      renderDetail();
    });

    var cb = document.getElementById("classbot-comment");
    if (cb) {
      cb.addEventListener("input", updateClassbotPreview);
      updateClassbotPreview();
    }

    document.getElementById("btn-save").addEventListener("click", saveCurrent);
    document.getElementById("btn-classbot").addEventListener("click", runClassbot);
    document.getElementById("btn-publish").addEventListener("click", openPublishModal);
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
    if (!state.activeKey) return Promise.resolve();
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
      .catch(alertError);
  }

  function runClassbot() {
    if (!state.activeKey) return;
    var model = els.modelSelect.value;
    api("/api/classbot/" + encodeURIComponent(state.activeKey), {
      method: "POST",
      body: { model: model, mode: "text" },
    })
      .then(function () { return loadRows().then(function () { selectRow(state.activeKey); }); })
      .catch(alertError);
  }

  function openPublishModal() {
    if (!state.detail) return;
    var grade = document.getElementById("final-grade").value;
    var instructor = document.getElementById("instructor-comment").value;
    var classbot = document.getElementById("classbot-comment").value;
    api("/api/compose-preview", {
      method: "POST",
      body: { instructor_comment: instructor, classbot_comment: classbot },
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
    if (!state.activeKey) return;
    var grade = document.getElementById("final-grade").value;
    saveCurrent().then(function () {
      return api("/api/publish/" + encodeURIComponent(state.activeKey), {
        method: "POST",
        body: { final_grade: grade },
      });
    }).then(function () {
      els.modal.classList.add("hidden");
      return loadRows().then(function () { selectRow(state.activeKey); });
    }).catch(alertError);
  });

  els.btnSync.addEventListener("click", function () {
    var key = els.filterAssignment.value;
    els.btnSync.disabled = true;
    var path = key ? "/api/sync" : "/api/sync-all";
    var body = key ? { assignment_key: key, force: true } : { force: true };
    api(path, { method: "POST", body: body })
      .then(function () { return loadRows(); })
      .catch(alertError)
      .finally(function () { els.btnSync.disabled = false; });
  });

  els.btnSeed.addEventListener("click", function () {
    api("/api/seed-demo", { method: "POST" })
      .then(function () { return loadRows(); })
      .catch(alertError);
  });

  els.btnBatch.addEventListener("click", function () {
    var pending = state.rows.filter(function (r) {
      return r.llm_status === "pending" || !r.llm_review_path;
    }).map(function (r) { return r.submission_key; });
    if (!pending.length) { alert("No pending rows."); return; }
    api("/api/classbot/batch", {
      method: "POST",
      body: { submission_keys: pending, model: els.modelSelect.value, mode: "text" },
    }).then(function () { return loadRows(); }).catch(alertError);
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
