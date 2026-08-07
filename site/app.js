const API_BASE_URL = (window.PVI_CONFIG?.apiBaseUrl || "").replace(/\/$/, "");

const EXAMPLE = {
  bedrooms: 4,
  bathrooms: 1.0,
  sqft_living: 1680,
  sqft_lot: 5043,
  floors: 1.5,
  waterfront: 0,
  view: 0,
  condition: 4,
  grade: 6,
  sqft_above: 1680,
  sqft_basement: 0,
  yr_built: 1911,
  yr_renovated: 0,
  zipcode: "98118",
  lat: 47.5354,
  long: -122.273,
  sqft_living15: 1560,
  sqft_lot15: 5765,
};

const FIELDS = [
  {name: "bedrooms", label: "Quartos", type: "int", min: 0, core: true},
  {name: "bathrooms", label: "Banheiros", type: "float", min: 0, step: 0.25, core: true},
  {name: "sqft_living", label: "Área habitável", type: "int", min: 0, suffix: "ft²", core: true},
  {name: "sqft_lot", label: "Área do terreno", type: "int", min: 0, suffix: "ft²", core: true},
  {name: "floors", label: "Pavimentos", type: "float", min: 0, step: 0.5, core: true},
  {name: "yr_built", label: "Ano de construção", type: "int", min: 0, core: true},
  {name: "zipcode", label: "ZIP code", type: "text", pattern: "\\d{5}", core: true},
  {name: "waterfront", label: "Frente para água", type: "select", options: [[0, "Não"], [1, "Sim"]]},
  {name: "view", label: "Avaliação da vista", type: "select", options: [[0,"0"],[1,"1"],[2,"2"],[3,"3"],[4,"4"]]},
  {name: "condition", label: "Condição geral", type: "select", options: [[1,"1"],[2,"2"],[3,"3"],[4,"4"],[5,"5"]]},
  {name: "grade", label: "Qualidade de construção", type: "int", min: 1, max: 13},
  {name: "sqft_above", label: "Área acima do solo", type: "int", min: 0, suffix: "ft²"},
  {name: "sqft_basement", label: "Área do porão", type: "int", min: 0, suffix: "ft²"},
  {name: "yr_renovated", label: "Ano da reforma", type: "int", min: 0, note: "0 = sem reforma registrada"},
  {name: "lat", label: "Latitude", type: "float", min: -90, max: 90, step: 0.0001},
  {name: "long", label: "Longitude", type: "float", min: -180, max: 180, step: 0.0001},
  {name: "sqft_living15", label: "Área habitável da vizinhança", type: "int", min: 0, suffix: "ft²"},
  {name: "sqft_lot15", label: "Terreno de referência da vizinhança", type: "int", min: 0, suffix: "ft²"},
];

function createField(definition) {
  const wrapper = document.createElement("div");
  wrapper.className = "form-field";

  const label = document.createElement("label");
  label.htmlFor = definition.name;
  label.textContent = definition.label;
  wrapper.appendChild(label);

  let input;
  if (definition.type === "select") {
    input = document.createElement("select");
    definition.options.forEach(([value, text]) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = text;
      input.appendChild(option);
    });
  } else {
    input = document.createElement("input");
    input.type = definition.type === "text" ? "text" : "number";
    if (definition.step !== undefined) input.step = String(definition.step);
    if (definition.min !== undefined) input.min = String(definition.min);
    if (definition.max !== undefined) input.max = String(definition.max);
    if (definition.pattern) input.pattern = definition.pattern;
    input.required = true;
  }
  input.id = definition.name;
  input.name = definition.name;
  wrapper.appendChild(input);

  const detail = definition.note || definition.suffix;
  if (detail) {
    const small = document.createElement("small");
    small.textContent = detail;
    wrapper.appendChild(small);
  }

  return wrapper;
}

function renderFields() {
  const core = document.getElementById("core-fields");
  const advanced = document.getElementById("advanced-fields");
  FIELDS.forEach((definition) => {
    (definition.core ? core : advanced).appendChild(createField(definition));
  });
  loadExample();
}

function loadExample() {
  Object.entries(EXAMPLE).forEach(([name, value]) => {
    const input = document.getElementById(name);
    if (input) input.value = String(value);
  });
}

function payloadFromForm() {
  return Object.fromEntries(FIELDS.map((field) => {
    const raw = document.getElementById(field.name).value;
    let value = raw;
    if (field.type === "int" || field.type === "select") value = Number.parseInt(raw, 10);
    if (field.type === "float") value = Number.parseFloat(raw);
    return [field.name, value];
  }));
}

function setPanel(state, message = "") {
  ["empty", "loading", "success", "error"].forEach((name) => {
    document.getElementById(`result-${name}`).classList.toggle("hidden", name !== state);
  });
  if (message) document.getElementById("error-message").textContent = message;
}

function setApiStatus(kind, message) {
  const dot = document.getElementById("status-dot");
  dot.classList.remove("online", "offline");
  if (kind) dot.classList.add(kind);
  document.getElementById("api-status").textContent = message;
}

function configureLinks() {
  const links = [document.getElementById("swagger-link"), document.getElementById("footer-api-link")];
  if (!API_BASE_URL) {
    links.forEach((link) => {
      link.href = "#demo";
      link.setAttribute("aria-disabled", "true");
    });
    document.getElementById("submit-prediction").disabled = true;
    setApiStatus("offline", "API pública ainda não conectada a esta versão do site.");
    return;
  }
  links.forEach((link) => {
    link.href = `${API_BASE_URL}/docs`;
    link.target = "_blank";
    link.rel = "noreferrer";
  });
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 90000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, {...options, signal: controller.signal});
  } finally {
    clearTimeout(timeout);
  }
}

async function checkHealth() {
  if (!API_BASE_URL) return;
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/health`, {}, 30000);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const health = await response.json();
    setApiStatus("online", `API online · modelo ${health.model_version}`);
  } catch (_) {
    setApiStatus("offline", "API indisponível no momento; tente novamente em instantes.");
  }
}

function readableApiError(payload, status) {
  if (Array.isArray(payload?.detail)) {
    const first = payload.detail[0];
    const location = Array.isArray(first?.loc) ? first.loc.slice(1).join(" → ") : "campo";
    return `Entrada inválida em ${location || "um campo"}: ${first?.msg || "revise os valores informados"}.`;
  }
  if (typeof payload?.detail === "string") return payload.detail;
  return `A API respondeu com HTTP ${status}.`;
}

async function submitPrediction(event) {
  event.preventDefault();
  if (!API_BASE_URL) return;
  const form = event.currentTarget;
  if (!form.reportValidity()) return;

  setPanel("loading");
  const button = document.getElementById("submit-prediction");
  button.disabled = true;

  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payloadFromForm()),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(readableApiError(payload, response.status));

    document.getElementById("estimated-price").textContent = new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: payload.currency || "USD",
      maximumFractionDigits: 0,
    }).format(payload.predicted_price);
    document.getElementById("result-model").textContent = payload.model_version;
    document.getElementById("result-request").textContent = payload.request_id;
    setPanel("success");
    setApiStatus("online", `API online · modelo ${payload.model_version}`);
  } catch (error) {
    const message = error?.name === "AbortError"
      ? "A API demorou mais que o esperado para responder. Aguarde alguns instantes e tente novamente."
      : (error?.message || "Falha inesperada ao consultar a API.");
    setPanel("error", message);
  } finally {
    button.disabled = false;
  }
}

function setupRevealAnimations() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const targets = [...document.querySelectorAll("[data-reveal]")];
  if (!targets.length || !("IntersectionObserver" in window)) return;

  document.documentElement.classList.add("motion-ready");
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, {threshold: 0.12, rootMargin: "0px 0px -8% 0px"});

  requestAnimationFrame(() => {
    targets.forEach((target) => {
      if (target.getBoundingClientRect().top < window.innerHeight * 0.92) {
        target.classList.add("is-visible");
      } else {
        observer.observe(target);
      }
    });
  });
}

renderFields();
configureLinks();
setupRevealAnimations();
document.getElementById("load-example").addEventListener("click", loadExample);
document.getElementById("prediction-form").addEventListener("submit", submitPrediction);
checkHealth();
