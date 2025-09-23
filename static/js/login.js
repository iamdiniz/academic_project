/**
 * DashTalent - Login JavaScript
 * Funcionalidades específicas da página de login
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".form-box");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    // Ofusca a senha no cliente antes de enviar (Base64)
    const senhaInput = document.querySelector("#senha");
    const emailInput = document.querySelector("#email");
    if (senhaInput && senhaInput.value) {
      try {
        const b64 = btoa(unescape(encodeURIComponent(senhaInput.value)));
        senhaInput.value = b64;
      } catch (_) {}
    }
    // Mantém o e-mail com nome neutro já definido no HTML
    // Fluxo segue normalmente
  });
});
