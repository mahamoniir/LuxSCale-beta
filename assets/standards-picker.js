/**
 * Links standards_keywords_upgraded.json (categories + search keywords) with
 * standards_cleaned.json (task_or_activity, ref_no, Em_r_lx, …).
 *
 * - Category datalist: from category_keywords keys (+ any category only in cleaned), or pass categoryLabels.
 * - Task datalist: task_or_activity rows in cleaned matching the selected category.
 * - Optional: categoryKeywords filters the category datalist as the user types (keyword or title match).
 */
(function () {
  function fillDatalist(datalistEl, values) {
    if (!datalistEl) return;
    datalistEl.innerHTML = "";
    values.forEach(function (v) {
      var opt = document.createElement("option");
      opt.value = v;
      datalistEl.appendChild(opt);
    });
  }

  function uniqueSortedCategoriesFromCleaned(rows) {
    var catSet = new Set();
    rows.forEach(function (r) {
      var c = r.category;
      if (c) catSet.add(c);
    });
    return Array.from(catSet).sort();
  }

  function mergeCategoryLists(keywordsObj, cleanedRows) {
    var set = new Set();
    if (keywordsObj && typeof keywordsObj === "object") {
      Object.keys(keywordsObj).forEach(function (k) {
        if (k) set.add(k);
      });
    }
    cleanedRows.forEach(function (r) {
      if (r.category) set.add(r.category);
    });
    return Array.from(set).sort();
  }

  function taskOptionsForCategory(rows, category) {
    var filtered = rows.filter(function (r) {
      return (r.category || "") === category;
    });
    var counts = new Map();
    filtered.forEach(function (r) {
      var t = (r.task_or_activity || "").trim();
      if (!t) return;
      counts.set(t, (counts.get(t) || 0) + 1);
    });
    var seen = new Set();
    var out = [];
    filtered.forEach(function (r) {
      var t = (r.task_or_activity || "").trim();
      if (!t) return;
      var value = t;
      if (counts.get(t) > 1) {
        value = t + " (" + (r.ref_no || "") + ")";
      }
      if (seen.has(value)) return;
      seen.add(value);
      out.push({ value: value, row: r });
    });
    return out;
  }

  function findRowForTaskValue(rows, category, taskValue) {
    var opts = taskOptionsForCategory(rows, category);
    for (var i = 0; i < opts.length; i++) {
      if (opts[i].value === taskValue) return opts[i].row;
    }
    var trimmed = (taskValue || "").trim();
    for (var j = 0; j < rows.length; j++) {
      var r = rows[j];
      if ((r.category || "") !== category) continue;
      if ((r.task_or_activity || "").trim() === trimmed) return r;
    }
    return null;
  }

  /**
   * Categories visible for current query: match category title or any keyword phrase.
   */
  function filterCategories(allCategories, categoryKeywords, query) {
    var q = (query || "").trim().toLowerCase();
    if (!q) return allCategories.slice();
    return allCategories.filter(function (cat) {
      if (cat.toLowerCase().indexOf(q) !== -1) return true;
      var kws = categoryKeywords && categoryKeywords[cat];
      if (!Array.isArray(kws)) return false;
      for (var i = 0; i < kws.length; i++) {
        if (String(kws[i]).toLowerCase().indexOf(q) !== -1) return true;
      }
      return false;
    });
  }

  window.initStandardsPicker = function (opts) {
    var cleanedUrl = opts.cleanedUrl || opts.jsonUrl || "standards/standards_cleaned.json";
    var keywordsUrl = opts.keywordsUrl || "standards/standards_keywords_upgraded.json";
    var skipKeywordsFetch = Array.isArray(opts.categoryLabels) && opts.categoryLabels.length > 0;
    var categoryInput = opts.categoryInput;
    var categoryDatalist = opts.categoryDatalist;
    var taskInput = opts.taskInput;
    var taskDatalist = opts.taskDatalist;
    var onRowResolved = typeof opts.onRowResolved === "function" ? opts.onRowResolved : function () {};
    var categoryKeywords = opts.categoryKeywords || null;
    var allCategoryLabels = [];
    var rows = [];

    function applyCategoryFilter() {
      var q = categoryInput ? categoryInput.value : "";
      var list = filterCategories(allCategoryLabels, categoryKeywords, q);
      if (list.length === 0 && q) list = allCategoryLabels.slice();
      fillDatalist(categoryDatalist, list);
    }

    var pCleaned =
      opts.cleanedRows && Array.isArray(opts.cleanedRows)
        ? Promise.resolve(opts.cleanedRows)
        : fetch(cleanedUrl).then(function (res) {
            if (!res.ok) throw new Error("Failed to load standards_cleaned: " + res.status);
            return res.json();
          });

    var pKeywords = skipKeywordsFetch
      ? Promise.resolve(null)
      : fetch(keywordsUrl)
          .then(function (res) {
            if (!res.ok) return null;
            return res.json();
          })
          .catch(function () {
            return null;
          });

    return Promise.all([pCleaned, pKeywords])
      .then(function (pair) {
        var data = pair[0];
        var kwDoc = pair[1];
        if (!Array.isArray(data)) throw new Error("standards_cleaned.json must be an array");
        rows = data;

        if (skipKeywordsFetch) {
          allCategoryLabels = opts.categoryLabels.slice().sort();
        } else if (kwDoc && kwDoc.category_keywords) {
          categoryKeywords = kwDoc.category_keywords;
          allCategoryLabels = mergeCategoryLists(categoryKeywords, rows);
        } else {
          allCategoryLabels = uniqueSortedCategoriesFromCleaned(rows);
        }

        fillDatalist(categoryDatalist, allCategoryLabels);

        function refreshTasks() {
          var cat = (categoryInput && categoryInput.value) || "";
          var opts = taskOptionsForCategory(rows, cat);
          fillDatalist(
            taskDatalist,
            opts.map(function (o) {
              return o.value;
            })
          );
          if (taskInput && cat) {
            var stillValid = opts.some(function (o) {
              return o.value === taskInput.value;
            });
            if (!stillValid) taskInput.value = "";
          }
        }

        function resolveSelection() {
          var cat = (categoryInput && categoryInput.value) || "";
          var taskVal = (taskInput && taskInput.value) || "";
          var row = findRowForTaskValue(rows, cat, taskVal);
          onRowResolved(row, { category: cat, taskValue: taskVal });
        }

        if (categoryInput) {
          categoryInput.addEventListener("change", function () {
            applyCategoryFilter();
            refreshTasks();
            resolveSelection();
          });
          categoryInput.addEventListener("input", function () {
            applyCategoryFilter();
            refreshTasks();
          });
        }
        if (taskInput) {
          taskInput.addEventListener("change", resolveSelection);
          taskInput.addEventListener("blur", resolveSelection);
        }

        refreshTasks();
        applyCategoryFilter();

        return {
          rows: rows,
          categoryKeywords: categoryKeywords,
          allCategoryLabels: allCategoryLabels,
          refreshTasks: refreshTasks,
          findRowForTaskValue: findRowForTaskValue
        };
      })
      .catch(function (err) {
        console.error(err);
        if (opts.onError) opts.onError(err);
      });
  };
})();
