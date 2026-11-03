const contactForm = document.getElementById("contact-form");
if (contactForm) {
  const recipient = "iivanvictor@outlook.com";
  const button = contactForm.querySelector('button[type="submit"]');
  const label = contactForm.querySelector(".contact-button-label");
  const note = document.getElementById("form-note");
  const status = document.getElementById("contact-status");
  const prepared = document.getElementById("prepared-email");
  const configured = (contactForm.getAttribute("action") || "").trim();
  const endpoint = /^https:\/\/formspree\.io\/f\/[a-zA-Z0-9]+$/.test(configured)
    ? configured
    : "";
  button.disabled = false;
  if (endpoint) {
    label.textContent = "Enviar mensagem";
    note.textContent =
      "Seus dados serão enviados ao Formspree para encaminhar a mensagem por e-mail. E-mail e WhatsApp também estão disponíveis ao lado.";
  }

  if (!endpoint) {
    label.textContent = "Preparar e-mail";
    note.textContent =
      "Prepare sua mensagem e abra o aplicativo de e-mail para concluir o envio. Nenhuma mensagem é enviada automaticamente por este formulário.";
  }

  function prepareEmail(data) {
    const body = `Nome: ${data.get("name")}\nE-mail: ${data.get("email")}\nCelular: ${data.get("phone") || "Não informado"}\n\n${data.get("message")}`;
    prepared.href = `mailto:${recipient}?subject=${encodeURIComponent("Contato pelo portfólio de Victor Azevedo")}&body=${encodeURIComponent(body)}`;
    prepared.hidden = false;
  }

  contactForm.addEventListener("input", () => {
    // A previously prepared link must not send stale field values.
    prepared.hidden = true;
    status.textContent = "";
  });

  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (button.disabled || !contactForm.reportValidity()) return;
    const data = new FormData(contactForm);
    prepareEmail(data);
    if (!endpoint) {
      status.textContent =
        "Mensagem preparada, ainda não enviada. Abra o aplicativo pelo link abaixo e confirme o envio nele.";
      prepared.focus();
      return;
    }
    button.disabled = true;
    const fields = contactForm.querySelectorAll(
      "input:not([type=hidden]), textarea",
    );
    fields.forEach((field) => {
      field.readOnly = true;
    });
    contactForm.setAttribute("aria-busy", "true");
    label.textContent = "Enviando…";
    status.textContent = "Enviando a mensagem ao serviço…";
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok || result.errors || result.ok === false)
        throw new Error("Submission not accepted");
      contactForm.reset();
      prepared.hidden = true;
      status.textContent =
        "Sua mensagem foi aceita pelo serviço de envio. Obrigado pelo contato!";
    } catch {
      status.textContent =
        "Não foi possível confirmar o envio. Sua mensagem foi preservada. Você pode usar o link de e-mail abaixo ou o WhatsApp.";
    } finally {
      clearTimeout(timeout);
      button.disabled = false;
      fields.forEach((field) => {
        field.readOnly = false;
      });
      label.textContent = "Enviar mensagem";
      contactForm.removeAttribute("aria-busy");
    }
  });
}
