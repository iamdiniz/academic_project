/**
 * Formulários e Validações
 * Gerencia validações de formulários e inputs
 */

// Validação de período (1-20)
function initPeriodoValidation() {
  const periodoInput = document.getElementById("periodo");
  if (periodoInput) {
    periodoInput.addEventListener("input", function () {
      let val = this.value.replace(/[^0-9]/g, "");
      if (val.length > 2) val = val.slice(0, 2);
      if (val !== "") {
        let num = parseInt(val, 10);
        if (num < 1) num = 1;
        if (num > 20) num = 20;
        this.value = num;
      } else {
        this.value = "";
      }
    });

    // Impede colar valores inválidos
    periodoInput.addEventListener("paste", function (e) {
      e.preventDefault();
    });
  }
}

// Validação de email
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Validação de telefone
function validatePhone(phone) {
  const re = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
  return re.test(phone);
}

// Inicializar validações quando DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
  initPeriodoValidation();
});
