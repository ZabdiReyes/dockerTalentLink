const uploadForm = document.getElementById("uploadForm");
const pdfInput = document.getElementById("pdfFiles");
const uploadStatus = document.getElementById("uploadStatus");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const files = pdfInput.files;
  if (files.length === 0) {
    uploadStatus.textContent = "No se han seleccionado archivos.";
    uploadStatus.style.color = "red";
    return;
  }

  if (files.length > 50) {
    uploadStatus.textContent = "Solo se permiten hasta 50 archivos.";
    uploadStatus.style.color = "red";
    return;
  }

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  uploadStatus.textContent = "Subiendo archivos...";
  uploadStatus.style.color = "black";

  try {
    console.log("API_BASE_URL:", API_BASE_URL);
    console.log("Fetch final:", `${API_BASE_URL}/upload-pdf/`);
    const response = await fetch(`${API_BASE_URL}/upload-pdf/`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Error en la respuesta del servidor");

    const result = await response.json();
    uploadStatus.textContent = result.detail || "Archivos subidos con éxito.";
    uploadStatus.style.color = "green";
    uploadForm.reset();
  } catch (err) {
    console.error(err);
    uploadStatus.textContent = "Error al subir archivos: " + err.message;
    uploadStatus.style.color = "red";
  }
});
