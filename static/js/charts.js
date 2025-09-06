/**
 * Gráficos e Visualizações
 * Gerencia criação e configuração de gráficos Chart.js
 */

// Criar gráfico radar para skills do aluno
function createSkillsChart(
  canvasId,
  hardLabels,
  hardSkills,
  softLabels,
  softSkills
) {
  const ctx = document.getElementById(canvasId).getContext("2d");

  return new Chart(ctx, {
    type: "radar",
    data: {
      labels: hardLabels.length > 0 ? hardLabels : softLabels,
      datasets: [
        {
          label: "Hard Skills",
          data: hardSkills,
          customLabels: hardLabels,
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          borderColor: "rgba(54, 162, 235, 1)",
          pointBackgroundColor: "rgba(54, 162, 235, 1)",
          borderWidth: 2,
        },
        {
          label: "Soft Skills",
          data: softSkills,
          customLabels: softLabels,
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          borderColor: "rgba(255, 99, 132, 1)",
          pointBackgroundColor: "rgba(255, 99, 132, 1)",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      interaction: {
        mode: "nearest",
        intersect: true,
      },
      scales: {
        r: {
          beginAtZero: true,
          min: 0,
          max: 10,
          ticks: {
            display: false,
            stepSize: 1,
            color: "#666",
            backdropColor: "rgba(255, 255, 255, 0.8)",
          },
          grid: {
            color: "rgba(200, 200, 200, 0.5)",
          },
          angleLines: {
            color: "rgba(200, 200, 200, 0.5)",
          },
          pointLabels: {
            callback: function (label, index) {
              const hard = hardLabels[index] ? `🟦 ${hardLabels[index]}` : "";
              const soft = softLabels[index] ? `🟥 ${softLabels[index]}` : "";
              return [hard, soft].filter(Boolean);
            },
            font: {
              size: 8,
            },
            color: "#000",
          },
        },
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: {
            color: "black",
          },
        },
        tooltip: {
          enabled: true,
          mode: "nearest",
          intersect: true,
          callbacks: {
            title: function () {
              return "";
            },
            label: function (context) {
              const dataset = context.dataset;
              const index = context.dataIndex;
              const customLabel = dataset.customLabels?.[index] || "Skill";
              const value = context.formattedValue;
              const cor = dataset.label === "Soft Skills" ? "🟥" : "🟦";
              return `${cor} ${customLabel}: ${value}`;
            },
          },
          backgroundColor: "rgba(0,0,0,0.8)",
          titleColor: "#fff",
          bodyColor: "#fff",
          displayColors: false,
        },
      },
    },
  });
}

// Criar gráfico de barras simples
function createBarChart(canvasId, labels, data, label, color) {
  const ctx = document.getElementById(canvasId).getContext("2d");

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: label,
          data: data,
          backgroundColor: color,
          borderColor: color,
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
}

// Inicializar gráficos quando DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
  // Os gráficos específicos serão inicializados pelos templates
  // que chamam as funções acima com os dados necessários
});

