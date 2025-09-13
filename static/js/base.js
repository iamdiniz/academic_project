/**
 * DashTalent - Base JavaScript
 * Funcionalidades comuns compartilhadas entre todas as páginas
 */

// Função global para exibir toasts de notificação
window.showToast = function (
  mensagem,
  cor = "success",
  tempo = 2500,
  icone = ""
) {
  const toast = document.getElementById("toastNotificacao");
  const toastBody = document.getElementById("toastNotificacaoBody");

  if (toast && toastBody) {
    toast.className = `toast align-items-center text-bg-${cor} border-0`;
    toastBody.innerHTML = icone + mensagem;
    const bsToast = new bootstrap.Toast(toast, { delay: tempo });
    bsToast.show();
  }
};

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Configuração do navbar mobile
  const navbarToggler = document.querySelector(".navbar-toggler");
  const navbarCollapse = document.getElementById("navbarContent");
  const brandMobile = document.getElementById("navbarBrandMobile");

  if (navbarToggler && navbarCollapse && brandMobile) {
    navbarCollapse.addEventListener("show.bs.collapse", function () {
      brandMobile.style.display = "none";
    });
    navbarCollapse.addEventListener("hide.bs.collapse", function () {
      brandMobile.style.display = "block";
    });
  }
});
