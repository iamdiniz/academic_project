/**
 * DashTalent - Acompanhar JavaScript
 * Funcionalidades específicas da página de acompanhamento de alunos
 */

// Função para abrir modal de status do aluno
function abrirStatus(id_aluno) {
  fetch("/status_aluno/" + id_aluno)
    .then((response) => response.text())
    .then((html) => {
      document.getElementById("statusBody").innerHTML = html;
      var myModal = new bootstrap.Modal(document.getElementById("statusModal"));
      myModal.show();
    });
}

// Função para abrir modal de confirmação de remoção
function abrirModalRemover(id_aluno) {
  const form = document.getElementById("formRemoverAcompanhamento");
  form.action = "/remover_acompanhamento/" + id_aluno;
  var modal = new bootstrap.Modal(
    document.getElementById("modalRemoverAcompanhamento")
  );
  modal.show();
}

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
