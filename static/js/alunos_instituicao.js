/**
 * DashTalent - Alunos Instituição JavaScript
 * Funcionalidades específicas da página de gerenciamento de alunos
 */

// Dados das hard skills por curso (passados pelo template HTML)
let hardSkillsPorCurso = window.hardSkillsPorCurso || {};
const cadastroModal = document.getElementById("cadastroModal");

// Função para renderizar campos de hard skills baseado no curso selecionado
function renderHardSkillsFields() {
  const cursoSelect = document.querySelector(
    '#cadastroModal select[name="curso"]'
  );
  const hardSkillsFields = document.getElementById("hardSkillsFields");
  if (!cursoSelect || !hardSkillsFields) return;

  const curso = cursoSelect.value;
  const hardSkills = hardSkillsPorCurso[curso] || [];

  hardSkillsFields.innerHTML = "";

  hardSkills.forEach((skill) => {
    const fieldName = "hard_" + skill.toLowerCase().replace(/ /g, "_");
    hardSkillsFields.innerHTML += `
            <div class="col-md-6">
                <label>${skill}</label>
                <input name="${fieldName}" type="number" class="form-control skill-input" min="0" max="10" step="1" required>
            </div>
        `;
  });
  applySkillInputValidation();
}

// Função para aplicar validação nos inputs de skills
function applySkillInputValidation() {
  const skillInputs = document.querySelectorAll("#cadastroModal .skill-input");
  skillInputs.forEach(function (input) {
    input.addEventListener("keydown", function (e) {
      // Permite teclas de controle
      if (
        e.key === "Backspace" ||
        e.key === "Tab" ||
        e.key === "Delete" ||
        e.key === "ArrowLeft" ||
        e.key === "ArrowRight" ||
        e.key === "Home" ||
        e.key === "End"
      ) {
        return;
      }
      // Permite apenas números de 0 a 9
      if (!/^[0-9]$/.test(e.key)) {
        e.preventDefault();
      }
      // Impede digitar mais de dois dígitos
      if (this.value.length >= 2 && this.selectionStart === this.selectionEnd) {
        e.preventDefault();
      }
    });

    input.addEventListener("input", function () {
      let value = this.value.replace(/[^0-9]/g, "");
      if (value.length > 2) value = value.slice(0, 2);
      if (parseInt(value) > 10) value = "10";
      this.value = value;
    });
  });
}

// Função para alternar erro visual nos campos
function toggleFieldError(input, condition, message) {
  const feedback = input.nextElementSibling;
  if (condition) {
    input.classList.add("is-invalid");
    if (feedback) feedback.textContent = message;
  } else {
    input.classList.remove("is-invalid");
    if (feedback) feedback.textContent = "";
  }
}

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Garante que ao abrir o modal, os campos estejam corretos
  cadastroModal.addEventListener("shown.bs.modal", renderHardSkillsFields);

  // Atualiza campos ao trocar o curso
  document.addEventListener("change", function (e) {
    if (e.target && e.target.matches('#cadastroModal select[name="curso"]')) {
      renderHardSkillsFields();
    }
  });

  // Validação inicial dos inputs de skills existentes
  const skillInputs = document.querySelectorAll("#cadastroModal .skill-input");
  skillInputs.forEach(function (input) {
    input.addEventListener("keydown", function (e) {
      // Permite teclas de controle
      if (
        e.key === "Backspace" ||
        e.key === "Tab" ||
        e.key === "Delete" ||
        e.key === "ArrowLeft" ||
        e.key === "ArrowRight" ||
        e.key === "Home" ||
        e.key === "End"
      ) {
        return;
      }
      // Permite apenas números de 0 a 9
      if (!/^[0-9]$/.test(e.key)) {
        e.preventDefault();
      }
      // Impede digitar mais de dois dígitos
      if (this.value.length >= 2 && this.selectionStart === this.selectionEnd) {
        e.preventDefault();
      }
    });

    input.addEventListener("input", function () {
      let value = this.value.replace(/[^0-9]/g, "");
      if (value.length > 2) value = value.slice(0, 2);
      if (parseInt(value) > 10) value = "10";
      this.value = value;
    });
  });

  // Validação completa do formulário de cadastro
  const form = document.querySelector("#cadastroModal form");
  if (!form) return;

  const nomeInput = form.querySelector('[name="nome_jovem"]');
  const dataInput = form.querySelector('[name="data_nascimento"]');
  const enderecoInput = form.querySelector('[name="endereco_jovem"]');
  const emailInput = form.querySelector('[name="email"]');
  const formacaoInput = form.querySelector('[name="formacao"]');
  const periodoInput = form.querySelector('[name="periodo"]');
  const contatoInput = document.getElementById("contato_jovem");

  // Aplica limites diretos nos inputs
  nomeInput.maxLength = 30;
  emailInput.maxLength = 50;
  formacaoInput.maxLength = 80;
  enderecoInput.maxLength = 150;

  // Impede números no nome
  nomeInput.addEventListener("input", function () {
    this.value = this.value.replace(/[^A-Za-zÀ-ú\s]/g, "").slice(0, 30);
    toggleFieldError(this, this.value.trim() === "", "Nome obrigatório.");
  });

  // Restringe número de 1 a 20 no período
  periodoInput.addEventListener("input", function () {
    let val = this.value.replace(/[^0-9]/g, "");
    if (val) {
      let num = parseInt(val, 10);
      if (num > 20) num = 20;
      if (num < 1) num = 1;
      this.value = num;
    } else {
      this.value = "";
    }
  });

  // Restringe idade mínima e máxima no campo data
  const hoje = new Date();
  const minDate = new Date(
    hoje.getFullYear() - 70,
    hoje.getMonth(),
    hoje.getDate()
  )
    .toISOString()
    .split("T")[0];
  const maxDate = new Date(
    hoje.getFullYear() - 17,
    hoje.getMonth(),
    hoje.getDate()
  )
    .toISOString()
    .split("T")[0];
  dataInput.setAttribute("min", minDate);
  dataInput.setAttribute("max", maxDate);

  // Validação do contato
  if (contatoInput) {
    contatoInput.addEventListener("input", function () {
      // Remove tudo que não for número
      this.value = this.value.replace(/\D/g, "").slice(0, 11);
    });
    contatoInput.addEventListener("keydown", function (e) {
      // Permite teclas de controle
      if (
        e.key === "Backspace" ||
        e.key === "Tab" ||
        e.key === "Delete" ||
        e.key === "ArrowLeft" ||
        e.key === "ArrowRight" ||
        e.key === "Home" ||
        e.key === "End"
      ) {
        return;
      }
      // Permite apenas números
      if (!/^[0-9]$/.test(e.key)) {
        e.preventDefault();
      }
    });
  }

  // Validação completa no submit
  form.addEventListener("submit", function (e) {
    let valido = true;

    // Validação nome
    if (!nomeInput.value.trim()) {
      toggleFieldError(nomeInput, true, "Nome obrigatório.");
      valido = false;
    } else if (!/^[A-Za-zÀ-ú\s]+$/.test(nomeInput.value)) {
      toggleFieldError(nomeInput, true, "Nome só pode conter letras.");
      valido = false;
    } else {
      toggleFieldError(nomeInput, false);
    }

    // Validação data de nascimento
    const dataVal = new Date(dataInput.value);
    if (
      !dataInput.value ||
      dataVal < new Date(minDate) ||
      dataVal > new Date(maxDate)
    ) {
      toggleFieldError(dataInput, true, "Data de nascimento inválida.");
      valido = false;
    } else {
      toggleFieldError(dataInput, false);
    }

    // Endereço
    if (!enderecoInput.value.trim()) {
      toggleFieldError(enderecoInput, true, "Endereço obrigatório.");
      valido = false;
    } else {
      toggleFieldError(enderecoInput, false);
    }

    // Contato
    const contatoLimpo = contatoInput.value.replace(/\D/g, "");
    if (contatoLimpo.length !== 11) {
      toggleFieldError(
        contatoInput,
        true,
        "Contato deve ter 11 dígitos no formato (00) 00000-0000."
      );
      valido = false;
    } else {
      toggleFieldError(contatoInput, false);
    }

    // Email
    if (
      !emailInput.value.trim() ||
      !emailInput.value.includes("@") ||
      !emailInput.value.includes(".")
    ) {
      toggleFieldError(emailInput, true, "Email inválido.");
      valido = false;
    } else {
      toggleFieldError(emailInput, false);
    }

    // Formação
    if (!formacaoInput.value.trim()) {
      toggleFieldError(formacaoInput, true, "Formação obrigatória.");
      valido = false;
    } else {
      toggleFieldError(formacaoInput, false);
    }

    // Período
    const periodoVal = parseInt(periodoInput.value);
    if (!periodoVal || periodoVal < 1 || periodoVal > 20) {
      toggleFieldError(periodoInput, true, "Período deve ser entre 1 e 20.");
      valido = false;
    } else {
      toggleFieldError(periodoInput, false);
    }

    // Hard skills e soft skills
    const hardInputs = form.querySelectorAll("#hardSkillsFields input");
    hardInputs.forEach((input) => {
      if (
        input.value === "" ||
        isNaN(input.value) ||
        input.value < 0 ||
        input.value > 10
      ) {
        toggleFieldError(input, true, "Nota deve ser de 0 a 10.");
        valido = false;
      } else {
        toggleFieldError(input, false);
      }
    });

    const softInputs = form.querySelectorAll(".skill-input");
    softInputs.forEach((input) => {
      if (
        input.value === "" ||
        isNaN(input.value) ||
        input.value < 0 ||
        input.value > 10
      ) {
        toggleFieldError(input, true, "Nota deve ser de 0 a 10.");
        valido = false;
      } else {
        toggleFieldError(input, false);
      }
    });

    if (!valido) {
      e.preventDefault();
      showToast(
        "Por favor, corrija os campos destacados em vermelho.",
        "danger",
        3500,
        '<i class="bi bi-x-circle-fill me-2"></i>'
      );
    }
  });

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML
});
