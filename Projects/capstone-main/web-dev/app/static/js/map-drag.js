window.settingDrag = function(panContainer) {
  let isDragging = false;
  let startX = 0, startY = 0;
  let offsetX = 0, offsetY = 0;

  const start = (e) => {
    const pt = e.touches?.[0] || e;
    startX = pt.clientX - offsetX;
    startY = pt.clientY - offsetY;
    isDragging = true;
    panContainer.style.cursor = "grabbing";
    e.preventDefault();
  };

  const drag = (e) => {
    if (!isDragging) return;
    const pt = e.touches?.[0] || e;
    offsetX = pt.clientX - startX;
    offsetY = pt.clientY - startY;
    panContainer.style.transform = `translate(${offsetX}px, ${offsetY}px)`;
    e.preventDefault();
  };

  const end = () => {
    isDragging = false;
    panContainer.style.cursor = "grab";
  };

  const resetDrag = () => {
    offsetX = 0;
    offsetY = 0;
    panContainer.style.transform = `translate(0px, 0px)`;
  };

  panContainer.style.cursor = "grab";
  panContainer.addEventListener("touchstart", start, { passive: false });
  window.addEventListener("touchmove", drag, { passive: false });
  window.addEventListener("touchend", end);

  return { resetDrag };
};
