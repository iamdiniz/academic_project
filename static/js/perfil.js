/**
 * DashTalent - Perfil JavaScript
 * Funcionalidades específicas da página de perfil
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Validação do formulário de perfil
  document.querySelector("form").addEventListener("submit", function (e) {
    let bloqueiaSubmit = false;

    // Validação customizada da senha
    const senhaInput = document.getElementById("senha");
    const erroSenha = document.getElementById("erro-senha");
    if (senhaInput && senhaInput.value) {
      if (senhaInput.value.length < 8) {
        senhaInput.classList.add("is-invalid");
        erroSenha.style.display = "block";
        bloqueiaSubmit = true;
      } else {
        senhaInput.classList.remove("is-invalid");
        erroSenha.style.display = "none";
      }
    } else {
      senhaInput.classList.remove("is-invalid");
      erroSenha.style.display = "none";
    }

    // Validação do cargo (chefe)
    const cargo = document.getElementById("cargo");
    if (cargo && !["CEO", "Gerente", "Coordenador"].includes(cargo.value)) {
      bloqueiaSubmit = true;
    }

    // Validação Bootstrap padrão
    if (!this.checkValidity()) {
      bloqueiaSubmit = true;
    }

    if (bloqueiaSubmit) {
      e.preventDefault();
      e.stopPropagation();
      // NÃO adiciona was-validated se houver erro customizado
      return;
    }

    // Só adiciona was-validated se tudo está ok
    this.classList.add("was-validated");
  });

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
