/**
 * First-party Extension demo worker (PHX-G43).
 * Requests declared invoke via host bridge; never elevates context or fetches network.
 */

(function () {
  function requestInvoke() {
    self.postMessage({
      type: "eaos.extension.invoke",
      action: "panel.render",
      surface: "extensions",
      channel: "worker",
    });
  }

  self.addEventListener("message", (event) => {
    const data = event.data;
    if (!data || typeof data !== "object") {
      return;
    }
    if (data.type === "eaos.extension.worker.ping") {
      requestInvoke();
      return;
    }
    if (data.type === "eaos.extension.invoke.result") {
      // Host acknowledgement — no privileged side effects.
      return;
    }
  });
})();
