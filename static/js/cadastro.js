/**
 * DashTalent - Cadastro JavaScript
 * Funcionalidades específicas da página de cadastro
 */

// Regex para validação de email
const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Função para exibir/ocultar campos baseado no tipo de usuário
function exibirCampos() {
  const tipo = document.getElementById("tipoUsuario").value;
  const blocoInstituicao = document.getElementById("camposInstituicao");
  const blocoChefe = document.getElementById("camposChefe");

  // Seleciona todos os campos de input, textarea e select
  const camposInstituicao = blocoInstituicao.querySelectorAll(
    'input:not([type="checkbox"]), textarea, select'
  );
  const camposChefe = blocoChefe.querySelectorAll("input, select");

  if (tipo === "instituicao") {
    blocoInstituicao.style.display = "block";
    blocoChefe.style.display = "none";
    camposInstituicao.forEach((campo) => (campo.required = true));
    camposChefe.forEach((campo) => (campo.required = false));
  } else if (tipo === "chefe") {
    blocoInstituicao.style.display = "none";
    blocoChefe.style.display = "block";
    camposChefe.forEach((campo) => (campo.required = true));
    camposInstituicao.forEach((campo) => (campo.required = false));
  } else {
    blocoInstituicao.style.display = "none";
    blocoChefe.style.display = "none";
    camposInstituicao.forEach((campo) => (campo.required = false));
    camposChefe.forEach((campo) => (campo.required = false));
  }
}

// Função para aplicar erro visual nos campos
function aplicarErro(input, mensagem, idErro) {
  const erroDiv = document.getElementById(idErro);
  if (mensagem) {
    input.classList.add("is-invalid");
    input.classList.remove("is-valid");
    erroDiv.textContent = mensagem;
  } else {
    input.classList.remove("is-invalid");
    input.classList.add("is-valid");
    erroDiv.textContent = "";
  }
}

// Função para validar campo obrigatório
function validarCampoObrigatorio(input, mensagem, idErro) {
  const valor = input.value.trim();
  const valido = valor !== "";
  aplicarErro(input, valido ? "" : mensagem, idErro);
  return valido;
}

// Função para validar campo com condição customizada
function validarCampo(input, condicao, mensagemErro, idErro) {
  const valido = condicao(input.value);
  aplicarErro(input, valido ? "" : mensagemErro, idErro);
  return valido;
}

// Função para filtrar entrada de texto (apenas letras ou números)
function filtrarEntrada(input, tipo) {
  const original = input.value;
  const filtrado =
    tipo === "letras"
      ? original.replace(/[^A-Za-zÀ-ÿ\s]/g, "")
      : original.replace(/[^0-9]/g, "");
  input.value = filtrado;

  aplicarErro(
    input,
    original !== filtrado
      ? tipo === "letras"
        ? "O campo só pode conter letras e espaços."
        : "Este campo só pode conter números."
      : "",
    "erro-" + input.id
  );
}

// Função para validar email
function validarEmail(input) {
  const email = input.value.trim();
  aplicarErro(
    input,
    email && !regexEmail.test(email) ? "Formato de e-mail inválido." : "",
    "erro-email"
  );
}

// Função para validar senha e mostrar força
function validarSenha(input) {
  const senha = input.value;
  aplicarErro(
    input,
    senha.length < 8 ? "A senha deve conter no mínimo 8 caracteres." : "",
    "erro-senha"
  );

  // Calcula força da senha
  let forca = 0;
  if (senha.length >= 8) forca++;
  if (/[A-Z]/.test(senha)) forca++;
  if (/[0-9]/.test(senha)) forca++;
  if (/[\W_]/.test(senha)) forca++;

  let texto = "",
    cor = "";
  switch (forca) {
    case 1:
    case 2:
      texto = "Senha fraca";
      cor = "text-danger";
      break;
    case 5:
      texto = "Senha média";
      cor = "text-warning";
      break;
    case 8:
      texto = "Senha forte";
      cor = "text-success";
      break;
  }

  const forcaEl = document.getElementById("forca-senha");
  if (forcaEl) {
    forcaEl.textContent = texto;
    forcaEl.className = `form-text ${cor}`;
  }

  validarConfirmacaoSenha();
}

// Função para validar confirmação de senha
function validarConfirmacaoSenha() {
  const senha = document.getElementById("senha").value;
  const confirmar = document.getElementById("confirmarSenha");

  aplicarErro(
    confirmar,
    confirmar.value && confirmar.value !== senha
      ? "As senhas não coincidem."
      : "",
    "erro-confirmarSenha"
  );
}

// Função para validar campos comuns (nome, email, senha)
function validarCamposComuns() {
  const nome = document.getElementById("nome");
  const email = document.getElementById("email");
  const senha = document.getElementById("senha");
  const confirmarSenha = document.getElementById("confirmarSenha");

  let valido = true;

  valido &= validarCampo(
    nome,
    (val) => /^[A-Za-zÀ-ÿ\s]{3,30}$/.test(val),
    "Nome inválido. Apenas letras entre 3 e 30 caracteres.",
    "erro-nome"
  );
  valido &= validarCampo(
    email,
    (val) => regexEmail.test(val.trim()) && val.length <= 50,
    "E-mail inválido.",
    "erro-email"
  );
  valido &= validarCampo(
    senha,
    (val) => val.length >= 8 && val.length <= 20,
    "Senha deve ter no mínimo 8 caracteres.",
    "erro-senha"
  );
  valido &= validarCampo(
    confirmarSenha,
    (val) => val === senha.value && val !== "",
    "As senhas não coincidem.",
    "erro-confirmarSenha"
  );

  return !!valido;
}

// Função para validar campos específicos de instituição
function validarCamposInstituicao() {
  const instituicaoNome = document.getElementById("instituicao_nome");
  const enderecoInstituicao = document.getElementById("endereco_instituicao");
  const cnpj = document.getElementById("cnpj");
  const infraestrutura = document.getElementById("infraestrutura");
  const notaMec = document.getElementById("nota_mec_input");
  const modalidades = document.getElementById("modalidades");
  const cursosSelecionados = document.querySelectorAll(
    'input[name="cursos_selecionados"]:checked'
  );

  let valido = true;

  valido &= validarCampo(
    instituicaoNome,
    (val) => /^[A-Za-zÀ-ÿ\s]{1,30}$/.test(val),
    "Nome inválido. Apenas letras até 30 caracteres.",
    "erro-instituicao_nome"
  );
  valido &= validarCampo(
    enderecoInstituicao,
    (val) => val.length <= 80 && val.length > 5,
    "Informe um endereço com no mínimo 5 caracteres.",
    "erro-endereco_instituicao"
  );
  valido &= validarCampo(
    cnpj,
    (val) => /^\d{14}$/.test(val),
    "CNPJ deve conter exatamente 14 números.",
    "erro-cnpj"
  );
  valido &= validarCampo(
    infraestrutura,
    (val) => val.length >= 20 && val.length <= 150,
    "Descreva a infraestrutura entre 20 e 150 caracteres.",
    "erro-infraestrutura"
  );
  valido &= validarCampo(
    notaMec,
    (val) => /^[1-5]$/.test(val),
    "Nota deve ser entre 1 e 5.",
    "erro-nota_mec_input"
  );
  valido &= validarCampo(
    modalidades,
    (val) => val !== "",
    "Selecione uma modalidade.",
    "erro-modalidades"
  );

  if (cursosSelecionados.length === 0) {
    showToast(
      "Selecione pelo menos um curso.",
      "danger",
      3500,
      '<i class="bi bi-exclamation-triangle-fill me-2"></i>'
    );
    valido = false;
  }

  return !!valido;
}

// Função para validar campos específicos de chefe
function validarCamposChefe() {
  const empresaNome = document.getElementById("empresa_nome");
  const cargo = document.getElementById("cargo");

  let valido = true;

  valido &= validarCampoObrigatorio(
    empresaNome,
    "O nome da empresa é obrigatório.",
    "erro-empresa_nome"
  );
  valido &= validarCampo(
    cargo,
    (val) => ["CEO", "Gerente", "Coordenador"].includes(val),
    "Selecione um cargo válido.",
    "erro-cargo"
  );

  return !!valido;
}

// Função principal de validação do formulário
function validarFormulario() {
  const tipoUsuario = document.getElementById("tipoUsuario").value;

  let valido = true;

  valido &= validarCamposComuns();

  if (tipoUsuario === "instituicao") {
    valido &= validarCamposInstituicao();
  } else if (tipoUsuario === "chefe") {
    valido &= validarCamposChefe();
  }

  if (!valido) {
    showToast(
      "Existem campos inválidos. Verifique e tente novamente.",
      "danger",
      3500,
      '<i class="bi bi-exclamation-triangle-fill"></i> '
    );
  }

  if (tipoUsuario !== "instituicao" && tipoUsuario !== "chefe") {
    showToast(
      "Selecione o tipo de cadastro.",
      "danger",
      3500,
      '<i class="bi bi-exclamation-triangle-fill"></i> '
    );
    return false;
  }

  return !!valido;
}

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Validação do campo nota MEC
  const notaInput = document.getElementById("nota_mec_input");
  if (notaInput) {
    // Bloqueia qualquer caractere que não seja número de 1 a 5
    notaInput.addEventListener("keydown", function (e) {
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
      // Permite apenas números de 1 a 5
      if (!/^[1-5]$/.test(e.key)) {
        e.preventDefault();
      }
      // Impede digitar mais de um dígito
      if (this.value.length >= 1 && this.selectionStart === this.selectionEnd) {
        e.preventDefault();
      }
    });

    // Impede colar valores inválidos
    notaInput.addEventListener("input", function () {
      let value = this.value.replace(/[^1-5]/g, "");
      if (value.length > 1) value = value[0];
      this.value = value;
    });
  }

  // Validação de cursos selecionados no submit
  document.querySelector(".form-box").addEventListener("submit", function (e) {
    const tipo = document.getElementById("tipoUsuario").value;
    if (tipo === "instituicao") {
      const checkboxes = document.querySelectorAll(
        'input[name="cursos_selecionados"]:checked'
      );
      if (checkboxes.length === 0) {
        showToast(
          "Selecione pelo menos um curso da instituição.",
          "danger",
          3500,
          '<i class="bi bi-exclamation-triangle-fill me-2"></i>'
        );
        e.preventDefault();
      }
    }
  });

  // Exibe toasts para mensagens flash do Flask
  // As mensagens flash são processadas no template HTML

  // Adiciona event listener para o select de tipo de usuário
  const tipoUsuarioSelect = document.getElementById("tipoUsuario");
  if (tipoUsuarioSelect) {
    tipoUsuarioSelect.addEventListener("change", function () {
      exibirCampos();
    });
  }

  // Garante que ao recarregar a página, os campos estejam corretos
  exibirCampos();

  // Adiciona event listeners para filtros de entrada
  const nomeInput = document.getElementById("nome");
  if (nomeInput) {
    nomeInput.addEventListener("input", function () {
      filtrarEntrada(this, "letras");
    });
  }

  const instituicaoNomeInput = document.getElementById("instituicao_nome");
  if (instituicaoNomeInput) {
    instituicaoNomeInput.addEventListener("input", function () {
      filtrarEntrada(this, "letras");
    });
  }

  const empresaNomeInput = document.getElementById("empresa_nome");
  if (empresaNomeInput) {
    empresaNomeInput.addEventListener("input", function () {
      filtrarEntrada(this, "letras");
    });
  }

  const cnpjInput = document.getElementById("cnpj");
  if (cnpjInput) {
    cnpjInput.addEventListener("input", function () {
      filtrarEntrada(this, "numeros");
    });
  }

  // Adiciona event listeners para validação de email
  const emailInput = document.getElementById("email");
  if (emailInput) {
    emailInput.addEventListener("blur", function () {
      validarEmail(this);
    });
  }

  // Adiciona event listeners para validação de senha
  const senhaInput = document.getElementById("senha");
  if (senhaInput) {
    senhaInput.addEventListener("input", function () {
      validarSenha(this);
    });
  }

  // Adiciona event listeners para validação de confirmação de senha
  const confirmarSenhaInput = document.getElementById("confirmarSenha");
  if (confirmarSenhaInput) {
    confirmarSenhaInput.addEventListener("input", function () {
      validarConfirmacaoSenha();
    });
  }
});
