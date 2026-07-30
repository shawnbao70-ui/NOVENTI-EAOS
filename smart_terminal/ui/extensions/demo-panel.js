/**
 * First-party Extension demo panel (PHX-G42).
 * Speaks only allowlisted postMessage; never sets trusted context.
 */

(function () {
  const status = document.getElementById("status");
  const button = document.getElementById("btnRequestRender");

  function setStatus(text) {
    if (status) {
      status.textContent = text;
    }
  }

  function requestRender() {
    if (!window.parent || window.parent === window) {
      setStatus("No host parent — bridge unavailable.");
      return;
    }
    window.parent.postMessage(
      {
        type: "eaos.extension.invoke",
        action: "panel.render",
        surface: "extensions",
      },
      "*"
    );
    setStatus("Requested panel.render via host bridge.");
  }

  window.addEventListener("message", (event) => {
    if (!event.data || typeof event.data !== "object") {
      return;
    }
    if (event.data.type !== "eaos.extension.invoke.result") {
      return;
    }
    setStatus(JSON.stringify(event.data, null, 2));
  });

  if (button) {
    button.addEventListener("click", requestRender);
  }
})();
