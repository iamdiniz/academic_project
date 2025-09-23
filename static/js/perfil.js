/**
 * DashTalent - Perfil JavaScript
 * Funcionalidades específicas da página de perfil
 */

// Regex para validação de email
const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


// Função para aplicar erro visual nos campos
function aplicarErro(input, mensagem, idErro) {
  const erroDiv = document.getElementById(idErro);
  if (mensagem) {
    input.classList.add("is-invalid");
    input.classList.remove("is-valid");
    if (erroDiv) erroDiv.textContent = mensagem;
  } else {
    input.classList.remove("is-invalid");
    input.classList.add("is-valid");
    if (erroDiv) erroDiv.textContent = "";
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

// Função para filtrar entrada de texto
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
  let mensagemErro = "";

  if (senha === "") {
    // Senha vazia: limpa erros e força
    aplicarErro(input, "", "erro-senha");
    const forcaDiv = document.getElementById("forca-senha");
    if (forcaDiv) {
      forcaDiv.textContent = "";
      forcaDiv.className = "form-text";
    }
    return true;
  }

  // Checagens obrigatórias se senha for preenchida
  if (senha.length < 8 || senha.length > 20) {
    mensagemErro += "A senha deve ter entre 8 e 20 caracteres. ";
  }
  if (!/[a-zA-Z]/.test(senha)) {
    mensagemErro += "Deve conter pelo menos uma letra. ";
  }
  if (!/[0-9]/.test(senha)) {
    mensagemErro += "Deve conter pelo menos um número. ";
  }
  if (!/[\W_]/.test(senha)) {
    mensagemErro += "Deve conter pelo menos um caractere especial (ex: !@#$%). ";
  }

  aplicarErro(input, mensagemErro.trim() || "", "erro-senha");

  // Calcula força da senha
  let forca = 0;
  if (senha.length >= 8 && senha.length <= 20) forca++;
  if (/[a-zA-Z]/.test(senha)) forca++;
  if (/[0-9]/.test(senha)) forca++;
  if (/[\W_]/.test(senha)) forca++;

  const forcaDiv = document.getElementById("forca-senha");
  if (forcaDiv) {
    let texto = "";
    let cor = "";
    switch (forca) {
      case 0:
      case 1:
        texto = "Senha muito fraca";
        cor = "text-danger";
        break;
      case 2:
        texto = "Senha fraca";
        cor = "text-warning";
        break;
      case 3:
        texto = "Senha média";
        cor = "text-info";
        break;
      case 4:
        texto = "Senha forte";
        cor = "text-success";
        break;
    }
    forcaDiv.textContent = texto;
    forcaDiv.className = `form-text ${cor}`;
  }

  return mensagemErro.trim() === "";
}

// Função para validar campos comuns
function validarCamposComuns() {
  const email = document.getElementById("email");
  const senha = document.getElementById("senha");

  let valido = true;

  if (email) {
    valido &= validarCampo(
      email,
      (val) => regexEmail.test(val.trim()) && val.length <= 50,
      "E-mail inválido.",
      "erro-email"
    );
  }

  if (senha) {
    // Senha é opcional, mas se preenchida, valida
    const senhaValida = senha.value === "" || validarSenha(senha);
    if (!senhaValida && senha.value !== "") {
      aplicarErro(
        senha,
        "A senha deve ter entre 8 e 20 caracteres, com pelo menos uma letra, um número e um caractere especial.",
        "erro-senha"
      );
    }
    valido &= senhaValida;
  }

  return !!valido;
}

// Função para detectar tipo de usuário baseado nos elementos do DOM
function detectarTipoUsuario() {
  if (document.getElementById("cargo")) {
    return "chefe";
  } else if (document.getElementById("nome_instituicao")) {
    return "instituicao";
  }
  return null;
}

// Função para validar campos específicos de chefe
function validarCamposChefe() {
  const nome = document.getElementById("nome");
  const cargo = document.getElementById("cargo");
  const nomeEmpresa = document.getElementById("nome_empresa");

  let valido = true;

  if (nome) {
    valido &= validarCampo(
      nome,
      (val) => /^[A-Za-zÀ-ÿ\s]{3,30}$/.test(val),
      "Nome inválido. Apenas letras entre 3 e 30 caracteres.",
      "erro-nome"
    );
  }

  if (cargo) {
    valido &= validarCampo(
      cargo,
      (val) => ["CEO", "Gerente", "Coordenador"].includes(val),
      "Selecione um cargo válido.",
      "erro-cargo"
    );
  }

  if (nomeEmpresa) {
    valido &= validarCampo(
      nomeEmpresa,
      (val) => /^[A-Za-zÀ-ÿ\s]{1,30}$/.test(val),
      "Nome inválido. Apenas letras até 30 caracteres.",
      "erro-nome_empresa"
    );
  }

  return !!valido;
}

// Função para validar campos específicos de instituição
function validarCamposInstituicao() {
  const nomeInstituicao = document.getElementById("nome_instituicao");
  const endereco = document.getElementById("endereco_instituicao");
  const reitor = document.getElementById("reitor");
  const infraestrutura = document.getElementById("infraestrutura");
  const notaMec = document.getElementById("nota_mec");
  const modalidades = document.getElementById("modalidades");

  let valido = true;

  if (nomeInstituicao) {
    valido &= validarCampo(
      nomeInstituicao,
      (val) => /^[A-Za-zÀ-ÿ\s]{1,30}$/.test(val),
      "Nome inválido. Apenas letras até 30 caracteres.",
      "erro-nome_instituicao"
    );
  }

  if (endereco) {
    valido &= validarCampo(
      endereco,
      (val) => val.length >= 5 && val.length <= 80,
      "Informe um endereço com no mínimo 5 e máximo 80 caracteres.",
      "erro-endereco_instituicao"
    );
  }

  if (reitor) {
    valido &= validarCampo(
      reitor,
      (val) => /^[A-Za-zÀ-ÿ\s]{3,30}$/.test(val),
      "Nome inválido. Apenas letras entre 3 e 30 caracteres.",
      "erro-reitor"
    );
  }

  if (infraestrutura) {
    valido &= validarCampo(
      infraestrutura,
      (val) => val.length >= 20 && val.length <= 150,
      "Descreva a infraestrutura entre 20 e 150 caracteres.",
      "erro-infraestrutura"
    );
  }

  if (notaMec) {
    valido &= validarCampo(
      notaMec,
      (val) => /^[1-5]$/.test(val),
      "Nota deve ser entre 1 e 5.",
      "erro-nota_mec"
    );
  }

  if (modalidades) {
    valido &= validarCampo(
      modalidades,
      (val) => val !== "" && ["Presencial", "Hi brido", "EAD"].includes(val),
      "Selecione uma modalidade válida.",
      "erro-modalidades"
    );
  }

  return !!valido;
}

// Função principal de validação do formulário
function validarFormulario() {
  const tipoUsuario = detectarTipoUsuario();

  if (!tipoUsuario) {
    showToast("Tipo de usuário não detectado.", "danger", 3500);
    return false;
  }

  let valido = true;

  valido &= validarCamposComuns();

  if (tipoUsuario === "chefe") {
    valido &= validarCamposChefe();
  } else if (tipoUsuario === "instituicao") {
    valido &= validarCamposInstituicao();
  }

  if (!valido) {
    showToast(
      "Existem campos inválidos. Verifique e tente novamente.",
      "danger",
      3500,
      '<i class="bi bi-exclamation-triangle-fill me-2"></i>'
    );
    return false;
  }

  return !!valido;
}

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Adiciona event listeners para filtros de entrada
  const inputsLetras = ["nome", "nome_empresa", "nome_instituicao", "reitor"];
  inputsLetras.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("input", function () {
        filtrarEntrada(this, "letras");
      });
    }
  });

  // Adiciona event listener para validação de email
  const emailInput = document.getElementById("email");
  if (emailInput) {
    emailInput.addEventListener("blur", function () {
      validarEmail(this);
    });
  }

  // Adiciona event listener para validação de senha
  const senhaInput = document.getElementById("senha");
  if (senhaInput) {
    senhaInput.addEventListener("input", function () {
      validarSenha(this);
    });
  }

  // Validação do formulário no submit 
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", function (e) {
      if (!validarFormulario()) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
      this.classList.add("was-validated");
    });
  }

  // Validação em tempo real para selects 
  const selects = ["cargo", "nota_mec", "modalidades"];
  selects.forEach(id => {
    const select = document.getElementById(id);
    if (select) {
      select.addEventListener("change", function () {
        const idErro = "erro-" + id;
        validarCampo(
          this,
          (val) => val !== "",
          "Campo obrigatório.",
          idErro
        );
      });
    }
  });

  // Validação em tempo real para textarea 
  const infraestrutura = document.getElementById("infraestrutura");
  if (infraestrutura) {
    infraestrutura.addEventListener("input", function () {
      validarCampo(
        this,
        (val) => val.length >= 20 && val.length <= 150,
        "Descreva a infraestrutura entre 20 e 150 caracteres.",
        "erro-infraestrutura"
      );
    });
  }

  // Validação em tempo real para endereço
  const endereco = document.getElementById("endereco_instituicao");
  if (endereco) {
    endereco.addEventListener("input", function () {
      validarCampo(
        this,
        (val) => val.length >= 5 && val.length <= 80,
        "Informe um endereço com no mínimo 5 e máximo 80 caracteres.",
        "erro-endereco_instituicao"
      );
    });
  }
});
