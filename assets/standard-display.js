/**
 * Maps standards_cleaned.json field keys to human-readable labels using
 * standards/aliases_upgraded.json (parameters.* synonym lists → primary label).
 */
(function (global) {
  var aliasesCache = null;

  /** Map cleaned JSON field → key under aliases.parameters */
  var CLEANED_TO_ALIAS_PARAM = {
    Em_r_lx: "average_lux",
    Em_u_lx: "max_lux",
    Uo: "uniformity",
    Ra: "color_rendering_ra",
    RUGL: "glare_ugr",
    Ez_lx: "min_lux"
  };

  function getParametersBlock(aliases) {
    var doc = aliases || aliasesCache || {};
    if (doc.parameters && typeof doc.parameters === "object" && !Array.isArray(doc.parameters)) {
      return doc.parameters;
    }
    if (doc.places && doc.places.parameters && typeof doc.places.parameters === "object") {
      return doc.places.parameters;
    }
    return {};
  }

  var FALLBACK_LABELS = {
    ref_no: "Reference no.",
    category: "Category",
    task_or_activity: "Task / activity",
    Em_r_lx: "Em,r (lx)",
    Em_u_lx: "Em,u (lx)",
    Uo: "Uo (uniformity)",
    Ra: "CRI (Ra — colour rendering index)",
    RUGL: "RUGL / UGR (glare)",
    Ez_lx: "Ez (lx)",
    Em_wall_lx: "Em wall (lx)",
    Em_ceiling_lx: "Em ceiling (lx)",
    specific_requirements: "Specific requirements",
    category_base: "Category base",
    category_sub: "Category sub",
    tasks: "Tasks (list)"
  };

  function loadAliasesUpgraded() {
    if (aliasesCache) return Promise.resolve(aliasesCache);
    return fetch("standards/aliases_upgraded.json")
      .then(function (res) {
        return res.ok ? res.json() : {};
      })
      .then(function (data) {
        aliasesCache = data && typeof data === "object" ? data : {};
        return aliasesCache;
      })
      .catch(function () {
        aliasesCache = {};
        return aliasesCache;
      });
  }

  function labelForStandardField(fieldKey, aliases) {
    if (fieldKey === "Uo") {
      return "Standard Uo (required)";
    }
    var params = getParametersBlock(aliases || aliasesCache);
    var pk = CLEANED_TO_ALIAS_PARAM[fieldKey];
    var list = pk && params[pk] ? params[pk] : null;
    if (list && list.length) {
      if (pk === "color_rendering_ra") {
        var hasCri = list.some(function (s) {
          return String(s).toLowerCase() === "cri";
        });
        return hasCri ? "CRI (Ra)" : String(list[0]) + " (" + fieldKey + ")";
      }
      if (pk === "glare_ugr") {
        var hasUgr = list.some(function (s) {
          return String(s).toLowerCase() === "ugr";
        });
        return hasUgr ? "UGR / RUGL (" + fieldKey + ")" : String(list[0]) + " (" + fieldKey + ")";
      }
      var primary = String(list[0]);
      var cap = primary.charAt(0).toUpperCase() + primary.slice(1);
      return cap + " (" + fieldKey + ")";
    }
    return FALLBACK_LABELS[fieldKey] || fieldKey;
  }

  var STANDARD_KEY_ORDER = [
    "ref_no",
    "category",
    "task_or_activity",
    "Em_r_lx",
    "Em_u_lx",
    "Uo",
    "Ra",
    "RUGL",
    "Ez_lx",
    "Em_wall_lx",
    "Em_ceiling_lx",
    "category_base",
    "category_sub",
    "specific_requirements",
    "tasks"
  ];

  function standardEntriesInOrder(sl) {
    if (!sl || typeof sl !== "object") return [];
    var seen = new Set();
    var out = [];
    STANDARD_KEY_ORDER.forEach(function (k) {
      if (!Object.prototype.hasOwnProperty.call(sl, k)) return;
      seen.add(k);
      out.push({ key: k, value: sl[k] });
    });
    Object.keys(sl).forEach(function (k) {
      if (seen.has(k)) return;
      out.push({ key: k, value: sl[k] });
    });
    return out;
  }

  function valueToDisplayString(v) {
    if (v === undefined || v === null) return "";
    if (Array.isArray(v)) return v.join("; ");
    return String(v);
  }

  global.LuxStandardDisplay = {
    loadAliasesUpgraded: loadAliasesUpgraded,
    labelForStandardField: labelForStandardField,
    standardEntriesInOrder: standardEntriesInOrder,
    valueToDisplayString: valueToDisplayString,
    getAliases: function () {
      return aliasesCache;
    }
  };
})(typeof window !== "undefined" ? window : this);
