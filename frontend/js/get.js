// ─────────────────── Elementos del DOM ───────────────────
const searchInput = document.getElementById("searchInput");
const tagList     = document.getElementById("tagList");
const searchBtn   = document.getElementById("searchBtn");
const resultsDiv  = document.getElementById("results");

// ─────────────────── Config & datos en memoria ───────────
const API_URL = "https://humble-halibut-rq4q66qxq5g2x699-8000.app.github.dev";
let tags = [];   // almacena strings:  skills, skills:python …

// 1ª categoría y secciones anidadas válidas
const etiquetasPrimera = new Set([
  "profile","title","skills","languages",
  "experience","education","achievements","others","contact"
]);
const seccionesValidas = new Set([
  "contact.name","contact.linkedin","contact.website",
  "contact.location","contact.company",
  "achievements.certifications","achievements.awards_honors",
  "achievements.publications","others.additional_information"
]);

// ─────────────────── Utilidades ───────────────────────────
const normalize = t => t.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();

function validarEtiqueta(tag) {
  if (tag.includes(":")) {
    const [etq] = tag.split(":");
    const eNorm = normalize(etq);
    return (etiquetasPrimera.has(eNorm) || seccionesValidas.has(eNorm));
  }
  const eNorm = normalize(tag);
  return (etiquetasPrimera.has(eNorm) || seccionesValidas.has(eNorm));
}

function buildSearchURL(query, tagsArr) {
  let url = `${API_URL}/buscar/?query=${encodeURIComponent(query.trim())}`;
  if (tagsArr.length) {
    url += `&tags=${encodeURIComponent(tagsArr.join(","))}`;
  }
  return url;
}

// ─────────────────── Captura de etiquetas (#) ─────────────
searchInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && searchInput.value.trim().startsWith("#")) {
    const raw = searchInput.value.trim().slice(1); // quita #
    if (validarEtiqueta(raw)) addTag(raw);
    searchInput.value = "";
  }
});

function addTag(tagStr) {
  const tagNorm = tagStr.toLowerCase();
  if (tags.includes(tagNorm)) return; // evitar duplicados
  tags.push(tagNorm);

  const span = document.createElement("span");
  span.className = "tag";
  span.textContent = tagStr;

  // color según lleve valor o no
  span.style.backgroundColor = tagStr.includes(":") ? "#388e3c" : "#81c784";

  // botón ✕
  const x = document.createElement("span");
  x.className = "tag-close";
  x.textContent = " ✕";
  x.onclick = () => {
    tagList.removeChild(span);
    tags = tags.filter(t => t !== tagNorm);
  };
  span.appendChild(x);
  tagList.appendChild(span);
}

// ─────────────────── Búsqueda ─────────────────────────────
searchBtn.addEventListener("click", async () => {
  const queryText = searchInput.value.trim();
  if (!queryText && !tags.length) {
    resultsDiv.innerHTML = "<p>Escribe una consulta o al menos una etiqueta.</p>";
    return;
  }

  // Construir URL
  const url = buildSearchURL(queryText, tags);
  console.log("URL:", url);

  // limpiar UI
  resultsDiv.innerHTML = "<p>Buscando…</p>";
  searchInput.value = "";

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("API error");
    const data = await res.json();

    if (!data.resultados?.length) {
      resultsDiv.innerHTML = "<p>No se encontraron coincidencias.</p>";
      return;
    }

    // ── Render CVs ────────────────────────────────────────
    resultsDiv.innerHTML = "";
    data.resultados.forEach((item, i) => {
      const cv        = item.cv || {};
      const contact   = cv.contact || {};
      const name      = contact.name || "Sin nombre";
      const linkedin  = contact.linkedin || "#";
      const title     = cv.title || "Sin título";
      const skills    = Array.isArray(cv.skills) ? cv.skills.join(", ") : "No especificadas";
      const languages = Array.isArray(cv.languages)
        ? cv.languages.map(l => typeof l === "string" ? l : l.language||"").filter(Boolean).join(", ")
        : "No especificados";

      const exp = (cv.experience?.[0]) ?
        `${cv.experience[0].position || "Cargo"} en ${cv.experience[0].company || "Empresa"} (${cv.experience[0].duration || "-"})`
        : "No disponible";

      const edu = (cv.education?.[0]) ?
        `${cv.education[0].degree || "Título"} en ${cv.education[0].institution || "Institución"} (${cv.education[0].duration || "-"})`
        : "No disponible";

      const safeLink = linkedin.startsWith("http") ? linkedin : `https://${linkedin}`;

      const card = document.createElement("div");
      card.className = "cv-card";
      card.innerHTML = `
        <h3>${name}</h3>
        <p><strong>Puesto:</strong> ${title}</p>
        <p><strong>LinkedIn:</strong> <a href="${safeLink}" target="_blank">${safeLink}</a></p>
        <p><strong>Habilidades:</strong> ${skills}</p>
        <p><strong>Idiomas:</strong> ${languages}</p>
        <p><strong>Última experiencia:</strong> ${exp}</p>
        <p><strong>Última educación:</strong> ${edu}</p>
        <p class="puntaje"><strong>Puntaje:</strong> ${data.puntuaciones?.[i]?.toFixed(2) || "N/A"}</p>
      `;
      resultsDiv.appendChild(card);
    });

  } catch (err) {
    console.error(err);
    resultsDiv.innerHTML = "<p>Error al buscar. Intenta de nuevo.</p>";
  }
});

// ── Mostrar / ocultar la guía de etiquetas ─────────────────
const helpBtn = document.getElementById("helpBtn");
const tagHelp = document.getElementById("tagHelp");

helpBtn.addEventListener("click", () => {
  tagHelp.classList.toggle("hidden");
});

document.addEventListener("click", (e) => {
  if (!tagHelp.contains(e.target) && e.target !== helpBtn) {
    tagHelp.classList.add("hidden");
  }
});
