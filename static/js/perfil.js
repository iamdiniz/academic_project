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

    // Neutraliza nomes para não expor esquema do banco (apenas nomes; valores permanecem)
    try {
      const isChefe = !!document.getElementById("cargo");
      if (isChefe) {
        const map = {
          nome: "p_n",
          email: "p_e",
          cargo: "p_r",
          nome_empresa: "p_c",
          senha: "p_s",
        };
        Object.keys(map).forEach((key) => {
          const el = document.querySelector(`[name="${key}"]`);
          if (el) el.setAttribute("name", map[key]);
        });
      } else {
        const map = {
          nome_instituicao: "i_n",
          reitor: "i_r",
          email: "i_e",
          endereco_instituicao: "i_addr",
          infraestrutura: "i_infra",
          nota_mec: "i_nota",
          modalidades: "i_mod",
          senha: "i_s",
        };
        Object.keys(map).forEach((key) => {
          const el = document.querySelector(`[name="${key}"]`);
          if (el) el.setAttribute("name", map[key]);
        });
      }
    } catch (_) {}
  });

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
