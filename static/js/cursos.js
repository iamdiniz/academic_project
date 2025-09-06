/**
 * Funcionalidades de Cursos
 * Gerencia validações e comportamentos específicos da página de cursos
 */

// Validação de curso duplicado
function initCursosValidation() {
  const form = document.querySelector("#cadastroCursosModal form");
  const selectCurso = document.getElementById("curso");

  if (form && selectCurso) {
    // Lista de cursos já cadastrados (passada pelo backend)
    const cursosAdicionados = window.cursosExistentes || [];

    form.addEventListener("submit", function (e) {
      const cursoSelecionado = selectCurso.value;
      if (cursosAdicionados.includes(cursoSelecionado)) {
        e.preventDefault();
        alert("Este curso já foi cadastrado!");
        selectCurso.focus();
      }
    });
  }
}

// Inicializar quando DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
  initCursosValidation();
});

