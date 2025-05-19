const searchInput = document.getElementById("searchInput");
const tagList = document.getElementById("tagList");
const searchBtn = document.getElementById("searchBtn");
const resultsDiv = document.getElementById("results");

let tags = [];

const etiquetasPrimera = new Set([
  "profile", "title", "skills", "languages",
  "experience", "education", "achievements", "others", "contact"
]);

const seccionesValidas = new Set([
  "contact.name", "contact.linkedin", "contact.website",
  "contact.location", "contact.company",
  "achievements.certifications", "achievements.awards_honors",
  "achievements.publications", "others.additional_information"
]);

function normalize(text) {
  return text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

function validarEtiqueta(tag) {
  if (tag.includes(":")) {
    const [etiqueta, ...resto] = tag.split(":");
    const valor = resto.join(":"); // permite valores con ":" dentro
    const etiquetaNorm = normalize(etiqueta);
    if (etiquetasPrimera.has(etiquetaNorm) || seccionesValidas.has(etiquetaNorm)) {
      return { valida: true, tipo: "con_valor", etiqueta: etiquetaNorm, valor };
    } else {
      return { valida: false };
    }
  } else {
    const etiquetaNorm = normalize(tag);
    if (etiquetasPrimera.has(etiquetaNorm) || seccionesValidas.has(etiquetaNorm)) {
      return { valida: true, tipo: "sin_valor", etiqueta: etiquetaNorm };
    } else {
      return { valida: false };
    }
  }
}

searchInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && this.value.trim() !== "") {
    const input = this.value.trim();
    if (input.startsWith("#")) {
      addTag(input.substring(1));
      this.value = "";
    }
  }
});

function addTag(tag) {
  const info = validarEtiqueta(tag); // No se normaliza aún el string completo
  const normTag = info.tipo === "con_valor"
    ? `${normalize(info.etiqueta)}:${info.valor}`  // Solo normaliza la etiqueta
    : normalize(tag);

  // Evitar duplicados en tags
  if (tags.includes(normTag)) return;

  const tagEl = document.createElement("span");
  tagEl.className = "tag";

  const closeBtn = document.createElement("span");
  closeBtn.className = "tag-close";
  closeBtn.textContent = " ✕";
  closeBtn.addEventListener("click", () => {
    tagList.removeChild(tagEl);
    tags = tags.filter((t) => t !== normTag);
  });

  if (!info.valida) {
    tagEl.style.backgroundColor = "#e74c3c"; // rojo
    tagEl.textContent = tag;
    tagEl.appendChild(closeBtn);
    tagList.appendChild(tagEl);
    return; // No lo añade a `tags`
  }

  tags.push(normTag);

  if (info.tipo === "sin_valor") {
    tagEl.style.backgroundColor = "#81c784"; // verde claro
    tagEl.textContent = tag;
  } else if (info.tipo === "con_valor") {
    tagEl.style.backgroundColor = "#388e3c"; // verde oscuro
    tagEl.innerHTML = `<strong>${info.etiqueta}:</strong> ${info.valor}`;
  }

  tagEl.appendChild(closeBtn);
  tagList.appendChild(tagEl);
}

searchBtn.addEventListener("click", async () => {
  let queryInput = searchInput.value.trim();

  if (!queryInput || queryInput.startsWith("#")) {
    resultsDiv.innerHTML = "<p>Por favor escribe una consulta antes de buscar.</p>";
    return;
  }

  // Limpiar etiquetas inválidas antes de enviar
  const nuevasTags = [];
  tags.forEach((t) => {
    const info = validarEtiqueta(t);
    if (info.valida) {
      nuevasTags.push(t);
    } else {
      // Eliminar visualmente la etiqueta inválida
      const tagSpans = [...tagList.children];
      tagSpans.forEach(el => {
        if (normalize(el.textContent.replace(" ✕", "")) === normalize(t)) {
          tagList.removeChild(el);
        }
      });
    }
  });
  tags = nuevasTags;

  const sectionTags = tags.filter(t => !t.includes(":"));
  const filterTags = tags.filter(t => t.includes(":"));

  const sections = sectionTags.join(",");
  const filters = filterTags.join(",");

  resultsDiv.innerHTML = "<p>Buscando...</p>";
  searchInput.value = "";

  try {
    const API_URL = "https://humble-halibut-rq4q66qxq5g2x699-8000.app.github.dev"; // <- sin slash
    const url = `${API_URL}/buscar/?query=${encodeURIComponent(queryInput)}&sections=${encodeURIComponent(sections)}&filters=${encodeURIComponent(filters)}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error("La API devolvió un error");

    const data = await response.json();
    resultsDiv.innerHTML = "";

    if (!data || !Array.isArray(data.resultados) || data.resultados.length === 0) {
      resultsDiv.innerHTML = "<p>No se encontraron coincidencias o la consulta fue vacía.</p>";
      return;
    }

    data.resultados.forEach((item, i) => {
      const cv = item.cv || {};
      const contact = cv.contact || {};
      const name = contact.name || "Sin nombre";
      const linkedin = contact.linkedin || "#";
      const title = cv.title || "Sin título";
      const skills = Array.isArray(cv.skills) ? cv.skills.join(", ") : "No especificadas";
      const languages = Array.isArray(cv.languages)
        ? cv.languages.map(l => typeof l === "string" ? l : l.language || "").filter(Boolean).join(", ")
        : "No especificados";

      const experience = Array.isArray(cv.experience) && cv.experience.length > 0
        ? `${cv.experience[0].position || "Cargo desconocido"} en ${cv.experience[0].company || "Empresa desconocida"} (${cv.experience[0].duration || "Duración no especificada"})`
        : "No disponible";

      const education = Array.isArray(cv.education) && cv.education.length > 0
        ? `${cv.education[0].degree || "Título desconocido"} en ${cv.education[0].institution || "Institución desconocida"} (${cv.education[0].duration || "Duración no especificada"})`
        : "No disponible";

      const safeLinkedin = linkedin.startsWith("http") ? linkedin : `https://${linkedin}`;

      const card = document.createElement("div");
      card.className = "cv-card";
      card.innerHTML = `
        <h3>${name}</h3>
        <p><strong>Puesto:</strong> ${title}</p>
        <p><strong>LinkedIn:</strong> <a href="${safeLinkedin}" target="_blank">${safeLinkedin}</a></p>

        <div style="margin-top: 10px;">
          <p><strong>Habilidades:</strong><br> ${skills}</p>
          <p><strong>Idiomas:</strong><br> ${languages}</p>
          <p><strong>Última experiencia:</strong><br> ${experience}</p>
          <p><strong>Última educación:</strong><br> ${education}</p>
          <p class="puntaje"><strong>Puntaje:</strong> ${data.puntuaciones?.[i]?.toFixed(2) || "N/A"}</p>
        </div>
      `;

      resultsDiv.appendChild(card);
    });


  } catch (error) {
    console.error("Error en fetch:", error);
    console.log("URL final:", url);
    console.log("Etiquetas:", tags);
    console.log("Query:", queryInput);
    resultsDiv.innerHTML = "<p>Error al buscar. Por favor intenta de nuevo.</p>";

  }
});
