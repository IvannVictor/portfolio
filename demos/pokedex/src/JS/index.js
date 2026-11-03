const button = document.getElementById("botao-alterar-tema");
button.addEventListener("click", () => {
  const dark = document.body.classList.toggle("modo-escuro");
  button.setAttribute("aria-pressed", String(dark));
  button.querySelector("img").src = dark
    ? "src/imagens/moon.png"
    : "src/imagens/sun.png";
});
