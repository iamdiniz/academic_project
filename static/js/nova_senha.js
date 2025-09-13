/**
 * DashTalent - Nova Senha JavaScript
 * Funcionalidades específicas da página de nova senha
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Validação em tempo real da confirmação de senha
  document
    .getElementById("confirmar_senha")
    .addEventListener("input", function () {
      const novaSenha = document.getElementById("nova_senha").value;
      const confirmarSenha = this.value;

      if (novaSenha && confirmarSenha && novaSenha !== confirmarSenha) {
        this.setCustomValidity("As senhas não coincidem");
      } else {
        this.setCustomValidity("");
      }
    });

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
