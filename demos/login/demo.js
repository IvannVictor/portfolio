document.querySelectorAll(".card-login [disabled]").forEach((control) => {
  control.disabled = false;
});
document.querySelector("form").addEventListener("submit", (event) => {
  event.preventDefault();
  document.getElementById("senha").value = "";
  document.querySelector(".login-feedback").textContent =
    "Interface demonstrada. Nenhuma autenticação foi realizada e nenhum dado foi enviado.";
});
