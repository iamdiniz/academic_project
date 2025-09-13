/**
 * DashTalent - Cursos JavaScript
 * Funcionalidades específicas da página de cursos
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("#cadastroCursosModal form");
  const selectCurso = document.getElementById("curso");

  // Lista de cursos já cadastrados (será passada pelo template HTML)
  const cursosAdicionados = [];

  // Validação de curso duplicado no submit
  form.addEventListener("submit", function (e) {
    const cursoSelecionado = selectCurso.value;
    if (cursosAdicionados.includes(cursoSelecionado)) {
      showToast(
        "Este curso já foi cadastrado!",
        "warning",
        3000,
        '<i class="bi bi-exclamation-triangle-fill me-2"></i>'
      );
      e.preventDefault();
    }
  });

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
