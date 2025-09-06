/**
 * Funcionalidades Gerais
 * JavaScript comum usado em toda a aplicação
 */

// Utilitários gerais
const AppUtils = {
  // Mostrar/ocultar loading
  showLoading: function (element) {
    if (element) {
      element.innerHTML =
        '<div class="spinner-border" role="status"><span class="visually-hidden">Carregando...</span></div>';
    }
  },

  hideLoading: function (element, originalContent) {
    if (element) {
      element.innerHTML = originalContent;
    }
  },

  // Formatar telefone
  formatPhone: function (input) {
    let value = input.value.replace(/\D/g, "");
    
    // Limitar a 11 dígitos
    if (value.length > 11) {
      value = value.slice(0, 11);
    }
    
    // Aplicar formatação baseada no tamanho
    if (value.length >= 11) {
      // Celular: (11) 99999-9999
      value = value.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
    } else if (value.length >= 7) {
      // Telefone fixo: (11) 9999-9999
      value = value.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3");
    } else if (value.length >= 3) {
      // Início: (11) 9
      value = value.replace(/(\d{2})(\d{0,5})/, "($1) $2");
    } else if (value.length >= 1) {
      // Apenas o DDD: (11
      value = value.replace(/(\d{0,2})/, "($1");
    }
    
    input.value = value;
  },

  // Formatar CPF
  formatCPF: function (input) {
    let value = input.value.replace(/\D/g, "");
    value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
    input.value = value;
  },

  // Validar CPF
  validateCPF: function (cpf) {
    cpf = cpf.replace(/\D/g, "");
    if (cpf.length !== 11) return false;

    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(cpf)) return false;

    // Validar dígitos verificadores
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(9))) return false;

    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    remainder = (sum * 10) % 11;
    if (remainder === 10 || remainder === 11) remainder = 0;
    if (remainder !== parseInt(cpf.charAt(10))) return false;

    return true;
  },
};

// Inicializar funcionalidades gerais quando DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
  // Formatação automática de telefone
  const phoneInputs = document.querySelectorAll(
    'input[type="tel"], input[name*="telefone"], input[name*="contato"]'
  );
  phoneInputs.forEach((input) => {
    input.addEventListener("input", function () {
      AppUtils.formatPhone(this);
    });
  });

  // Formatação automática de CPF
  const cpfInputs = document.querySelectorAll('input[name*="cpf"]');
  cpfInputs.forEach((input) => {
    input.addEventListener("input", function () {
      AppUtils.formatCPF(this);
    });
  });

  // Validação de formulários
  const forms = document.querySelectorAll('form[data-validate="true"]');
  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      const cpfInput = form.querySelector('input[name*="cpf"]');
      if (cpfInput && !AppUtils.validateCPF(cpfInput.value)) {
        e.preventDefault();
        alert("CPF inválido!");
        cpfInput.focus();
      }
    });
  });
});
