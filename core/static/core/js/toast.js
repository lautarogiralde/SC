document.addEventListener("DOMContentLoaded", function () {
  const toastElements = document.querySelectorAll(".toast");
  // Comprobamos de entrada si Bootstrap está cargado para no iterar en vano
  if (typeof bootstrap === "undefined" || !bootstrap.Toast) {
    console.warn("Bootstrap JS no está cargado o no incluye el módulo Toast.");
    return;
  }
  toastElements.forEach(function (toastElement) {
    // Inicializamos o recuperamos la instancia existente
    const toast = bootstrap.Toast.getOrCreateInstance(toastElement);
    toast.show();
  });
});
