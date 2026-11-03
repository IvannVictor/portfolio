const form = document.querySelector(".task-form");
const input = document.getElementById("nova-tarefa");
const list = document.querySelector(".list-task");
const feedback = document.querySelector(".task-feedback");
const storageKey = "portfolio.demo.tasks.v1";
let tasks = [];
let canSave = true;
try {
  const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
  if (!Array.isArray(saved)) throw new Error("Invalid task list");
  tasks = saved
    .filter(
      (task) =>
        task &&
        typeof task.tarefa === "string" &&
        typeof task.concluida === "boolean",
    )
    .map((task) => ({
      tarefa: task.tarefa.slice(0, 200),
      concluida: task.concluida,
    }));
} catch {
  feedback.textContent =
    "Não foi possível recuperar as tarefas salvas. A lista está vazia.";
}

function save(message) {
  try {
    localStorage.setItem(storageKey, JSON.stringify(tasks));
    canSave = true;
  } catch {
    canSave = false;
  }
  feedback.textContent =
    message +
    (canSave
      ? ""
      : " O navegador não permitiu salvar; as alterações durarão apenas nesta sessão.");
}

function render() {
  list.replaceChildren();
  if (!tasks.length) {
    const empty = document.createElement("li");
    empty.className = "empty-state";
    empty.textContent = "Nenhuma tarefa por aqui. Que tal começar uma?";
    list.append(empty);
  }
  tasks.forEach((task, index) => {
    const item = document.createElement("li");
    item.className = "task" + (task.concluida ? " done" : "");
    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.textContent = task.concluida ? "✓" : "○";
    toggle.setAttribute(
      "aria-label",
      (task.concluida ? "Reabrir " : "Concluir ") + task.tarefa,
    );
    toggle.setAttribute("aria-pressed", String(task.concluida));
    toggle.addEventListener("click", () => {
      task.concluida = !task.concluida;
      save(task.concluida ? "Tarefa concluída." : "Tarefa reaberta.");
      render();
      list.querySelectorAll(".task")[index].querySelector("button").focus();
    });
    const text = document.createElement("p");
    text.textContent = task.tarefa;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "×";
    remove.setAttribute("aria-label", "Excluir " + task.tarefa);
    remove.addEventListener("click", () => {
      tasks.splice(index, 1);
      save("Tarefa excluída.");
      render();
      const next =
        list.querySelectorAll(".task")[Math.min(index, tasks.length - 1)];
      if (next) next.querySelector("button").focus();
      else input.focus();
    });
    item.append(toggle, text, remove);
    list.append(item);
  });
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const value = input.value.trim();
  if (!value) {
    feedback.textContent = "Digite uma tarefa antes de adicionar.";
    input.focus();
    return;
  }
  tasks.push({ tarefa: value, concluida: false });
  input.value = "";
  save("Tarefa adicionada.");
  render();
  input.focus();
});
render();
