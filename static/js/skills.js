/**
 * Skills e Habilidades
 * Gerencia seleção e exibição de skills
 */

// Atualizar texto das skills selecionadas
function updateSelectedSkillsText() {
  const checked = document.querySelectorAll(".skill-checkbox:checked");
  const selected = Array.from(checked).map(
    (cb) => cb.parentElement.querySelectorAll("span")[1].innerText
  );

  let displayText = "";
  if (selected.length === 0) {
    displayText = "Selecione habilidades...";
  } else if (selected.length <= 2) {
    displayText = selected.join(", ");
  } else {
    displayText = selected.slice(0, 2).join(", ") + ` +${selected.length - 2}`;
  }

  const skillsTextElement = document.getElementById("selectedSkillsText");
  if (skillsTextElement) {
    skillsTextElement.innerText = displayText;
  }
}

// Atualizar texto das hard skills selecionadas
function updateSelectedHardSkillsText() {
  const checked = document.querySelectorAll(".hard-skill-checkbox:checked");
  const selected = Array.from(checked).map(
    (cb) => cb.parentElement.querySelectorAll("span")[1].innerText
  );

  const hardSkillsTextElement = document.getElementById(
    "selectedHardSkillsText"
  );
  if (hardSkillsTextElement) {
    hardSkillsTextElement.innerText = selected.length
      ? selected.join(", ")
      : "Selecionar...";
  }
}

// Atualizar texto das soft skills selecionadas
function updateSelectedSoftSkillsText() {
  const checked = document.querySelectorAll(".soft-skill-checkbox:checked");
  const selected = Array.from(checked).map(
    (cb) => cb.parentElement.querySelectorAll("span")[1].innerText
  );

  const softSkillsTextElement = document.getElementById(
    "selectedSoftSkillsText"
  );
  if (softSkillsTextElement) {
    softSkillsTextElement.innerText = selected.length
      ? selected.join(", ")
      : "Selecionar...";
  }
}

// Inicializar listeners de skills
function initSkillsListeners() {
  // Skills gerais
  document.querySelectorAll(".skill-checkbox").forEach((cb) => {
    cb.addEventListener("change", updateSelectedSkillsText);
  });

  // Hard skills
  document.querySelectorAll(".hard-skill-checkbox").forEach((cb) => {
    cb.addEventListener("change", updateSelectedHardSkillsText);
  });

  // Soft skills
  document.querySelectorAll(".soft-skill-checkbox").forEach((cb) => {
    cb.addEventListener("change", updateSelectedSoftSkillsText);
  });
}

// Inicializar quando DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
  initSkillsListeners();
  updateSelectedSkillsText();
  updateSelectedHardSkillsText();
  updateSelectedSoftSkillsText();
});

