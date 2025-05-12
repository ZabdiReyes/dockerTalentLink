const searchInput = document.getElementById("searchInput");
const tagList = document.getElementById("tagList");
const searchBtn = document.getElementById("searchBtn");
const resultsDiv = document.getElementById("results");

let tags = [];

function normalize(text) {
  return text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

searchInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && this.value.trim() !== "") {
    const input = this.value.trim();
    if (input.startsWith("#")) {
      addTag(input.substring(1));
      this.value = "";
    }
    // Si no empieza con #, no se borra, se deja para que se use como query al buscar
  }
});

function addTag(tag) {
  const normTag = normalize(tag);
  if (!tags.includes(normTag)) {
    tags.push(normTag);
    const tagEl = document.createElement("span");
    tagEl.className = "tag";
    tagEl.textContent = tag;

    const closeBtn = document.createElement("span");
    closeBtn.className = "tag-close";
    closeBtn.textContent = " ✕";
    closeBtn.addEventListener("click", () => {
      tagList.removeChild(tagEl);
      tags = tags.filter((t) => t !== normTag);
    });

    tagEl.appendChild(closeBtn);
    tagList.appendChild(tagEl);
  }
}

searchBtn.addEventListener("click", async () => {
  let queryInput = searchInput.value.trim();

  if (!queryInput || queryInput.startsWith("#")) {
    resultsDiv.innerHTML = "<p>Por favor escribe una consulta antes de buscar.</p>";
    return;
  }

  resultsDiv.innerHTML = "<p>Buscando...</p>";
  searchInput.value = ""; // limpiar el campo visualmente

  try {
    const url = `http://127.0.0.1:8000/buscar/?query=${encodeURIComponent(queryInput)}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("La API devolvió un error");

    const data = await response.json();
    resultsDiv.innerHTML = "";

    if (!data || !Array.isArray(data.resultados) || data.resultados.length === 0) {
      resultsDiv.innerHTML = "<p>No se encontraron coincidencias o la consulta fue vacía.</p>";
      return;
    }

    data.resultados.forEach((cv, i) => {
      const card = document.createElement("div");
      card.className = "cv-card";
      card.innerHTML = `
        <h3>${cv.contact?.name || "Sin nombre"}</h3>
        <p><strong>${cv.title || "Sin título"}</strong></p>
        <p><a href="https://${cv.contact?.linkedin}" target="_blank">LinkedIn</a></p>
        <p><strong>Habilidades:</strong> ${(cv.skills || []).join(", ")}</p>
        <p><strong>Puntaje:</strong> ${data.puntuaciones?.[i]?.toFixed(2) || "N/A"}</p>
      `;
      resultsDiv.appendChild(card);
    });
  } catch (error) {
    console.error("Error en fetch:", error);
    resultsDiv.innerHTML =
      "<p>Error al conectarse con la API. ¿Está corriendo en http://127.0.0.1:8000?</p>";
  }
});