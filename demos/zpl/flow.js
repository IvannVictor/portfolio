(() => {
  "use strict";
  const stages = [
    {title:"1. Recebimento do arquivo",description:"O operador disponibiliza um arquivo ZPL, TXT ou PDF para processamento. Para PDF, o aplicativo pode converter a etiqueta em comandos ZPL.",evidence:"Exemplo: etiqueta fictícia dos Correios, sem dados de destinatário."},
    {title:"2. Identificação e duplicidade",description:"O sistema identifica o tipo da etiqueta e verifica a chave de duplicidade no histórico. Para Correios, a referência é o código de rastreio; para mini DANFE, a combinação de nota fiscal e tipo.",evidence:"Exemplo: rastreio AA123456789BR; o resultado dependeria do histórico existente."},
    {title:"3. Envio ao spooler",description:"Se o processamento for permitido, o aplicativo encaminha comandos de impressão para a fila do Windows e registra o resultado do envio.",evidence:"O aceite da fila não é confirmação de que a etiqueta saiu fisicamente da impressora."},
    {title:"4. Histórico e rastreabilidade",description:"O aplicativo registra eventos para consulta, controle de duplicidade e análise de pendências. Ocorrências podem exigir conferência e reconciliação pelo operador.",evidence:"Eventos exibidos nesta demonstração são apenas ilustrativos; não há histórico real."}
  ];
  const title = document.getElementById("step-title");
  const description = document.getElementById("step-description");
  const evidence = document.getElementById("step-evidence");
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  const restart = document.getElementById("restart");
  const steps = [...document.querySelectorAll("[data-step]")];
  if (!title || !description || !evidence || !previous || !next || !restart || steps.length !== stages.length) return;
  let current = 0;
  function render() {
    const stage = stages[current];
    title.textContent = stage.title;
    description.textContent = stage.description;
    evidence.textContent = stage.evidence;
    previous.disabled = current === 0;
    next.disabled = current === stages.length - 1;
    next.textContent = next.disabled ? "Fluxo concluído" : "Próxima etapa";
    steps.forEach((element, index) => {
      if (index === current) element.setAttribute("aria-current", "step");
      else element.removeAttribute("aria-current");
      element.classList.toggle("complete", index < current);
    });
  }
  previous.addEventListener("click", () => { current = Math.max(0, current - 1); render(); });
  next.addEventListener("click", () => { current = Math.min(stages.length - 1, current + 1); render(); });
  restart.addEventListener("click", () => { current = 0; render(); });
  render();
})();