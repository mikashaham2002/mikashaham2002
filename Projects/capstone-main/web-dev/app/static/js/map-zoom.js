(function () {
  let scale = 1;
  const ZOOM_STEP = 0.2;
  const MIN_SCALE = 0.5;
  const MAX_SCALE = 3;

  function applyZoom() {
    const svg = document.querySelector("#svg-map svg");
    if (!svg) return;
    svg.style.transform = `scale(${scale})`;
    svg.style.transformOrigin = "center center";
  }

  function zoomIn() {
    if (scale < MAX_SCALE) {
      scale += ZOOM_STEP;
      applyZoom();
    }
  }

  function zoomOut() {
    if (scale > MIN_SCALE) {
      scale -= ZOOM_STEP;
      applyZoom();
    }
  }

  function resetZoom() {
    scale = 1;
    applyZoom();
  }

  document.addEventListener("DOMContentLoaded", () => {
    const zoomInBtn = document.getElementById("zoom-in");
    const zoomOutBtn = document.getElementById("zoom-out");
    const resetBtn = document.getElementById("reset");

    if (zoomInBtn) zoomInBtn.addEventListener("click", zoomIn);
    if (zoomOutBtn) zoomOutBtn.addEventListener("click", zoomOut);
    if (resetBtn) if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        resetZoom();
        dragControls.resetDrag();
      });}
  });
})();
