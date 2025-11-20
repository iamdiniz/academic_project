/**
 * DashTalent - Nova Senha JavaScript
 * Funcionalidades específicas da página de nova senha
 */

const PASSWORD_POLICY_MESSAGE =
  "A senha deve ter pelo menos 10 caracteres e incluir letras maiúsculas, letras minúsculas, números e caracteres especiais.";

function avaliarRequisitosSenhaNova(senha) {
  const valor = senha || "";
  return {
    comprimento: valor.length >= 10,
    maiuscula: /[A-Z]/.test(valor),
    minuscula: /[a-z]/.test(valor),
    digito: /\d/.test(valor),
    especial: /[^A-Za-z0-9]/.test(valor),
  };
}

function senhaNovaAtendePolitica(senha) {
  const requisitos = avaliarRequisitosSenhaNova(senha);
  return Object.values(requisitos).every(Boolean);
}

function atualizarChecklistSenhaNova(requisitos, checklistId) {
  const checklist = document.getElementById(checklistId);
  const policyContainer = checklist?.closest(".password-policy");
  if (!checklist || !policyContainer) return;

  const todosAtendidos = Object.values(requisitos).every(Boolean);
  const senhaVazia = !document.getElementById("nova_senha")?.value;

  // Se senha vazia, oculta tudo
  if (senhaVazia) {
    policyContainer.classList.add("hidden");
    return;
  }

  policyContainer.classList.remove("hidden");

  // Atualiza cada item do checklist
  checklist.querySelectorAll("[data-req]").forEach((item) => {
    const chave = item.dataset.req;
    const cumprido = requisitos[chave];
    item.classList.toggle("met", Boolean(cumprido));
  });

  // Se todos atendidos, mostra mensagem de sucesso e oculta checklist
  if (todosAtendidos) {
    let successMsg = policyContainer.querySelector(".password-policy__success");
    if (!successMsg) {
      successMsg = document.createElement("div");
      successMsg.className = "password-policy__success";
      successMsg.textContent = "Senha atende todos os requisitos";
      policyContainer.insertBefore(successMsg, checklist);
    }
    successMsg.style.display = "flex";
    checklist.classList.add("hidden");
  } else {
    // Se não todos atendidos, mostra checklist e oculta mensagem de sucesso
    const successMsg = policyContainer.querySelector(".password-policy__success");
    if (successMsg) successMsg.style.display = "none";
    checklist.classList.remove("hidden");
  }
}

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  const novaSenhaInput = document.getElementById("nova_senha");
  const confirmarSenhaInput = document.getElementById("confirmar_senha");

  function validarConfirmacaoNovaSenha() {
    if (!novaSenhaInput || !confirmarSenhaInput) return;
    if (
      confirmarSenhaInput.value &&
      confirmarSenhaInput.value !== novaSenhaInput.value
    ) {
      confirmarSenhaInput.setCustomValidity("As senhas não coincidem");
    } else {
      confirmarSenhaInput.setCustomValidity("");
    }
  }

  if (novaSenhaInput) {
    novaSenhaInput.addEventListener("input", function () {
      const requisitos = avaliarRequisitosSenhaNova(this.value);
      atualizarChecklistSenhaNova(requisitos, "passwordChecklistNova");

      if (senhaNovaAtendePolitica(this.value)) {
        this.setCustomValidity("");
      } else {
        this.setCustomValidity(PASSWORD_POLICY_MESSAGE);
      }

      validarConfirmacaoNovaSenha();
    });
  }

  if (confirmarSenhaInput) {
    confirmarSenhaInput.addEventListener("input", validarConfirmacaoNovaSenha);
  }

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
