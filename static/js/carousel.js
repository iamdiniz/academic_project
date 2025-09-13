/**
 * DashTalent - Carousel JavaScript
 * Funcionalidades específicas da página inicial/carousel
 */

// Inicialização quando o DOM estiver carregado
document.addEventListener("DOMContentLoaded", function () {
  // Configuração do Intersection Observer para animações de scroll
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("active");
        }
      });
    },
    {
      threshold: 0.2, // 20% do elemento visível já dispara a animação
    }
  );

  // Observa todos os elementos com classe scroll-anim
  document.querySelectorAll(".scroll-anim").forEach((el) => {
    observer.observe(el);
  });
});
