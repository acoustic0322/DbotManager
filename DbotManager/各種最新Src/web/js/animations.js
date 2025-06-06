// Reveal animations on scroll
function handleRevealAnimations() {
  const revealElements = document.querySelectorAll(
    ".reveal-left, .reveal-right"
  );

  const revealThreshold = 0.1; // Percentage of element visible

  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("active");
          revealObserver.unobserve(entry.target); // Stop observing once revealed
        }
      });
    },
    {
      threshold: revealThreshold,
    }
  );

  revealElements.forEach((element) => {
    revealObserver.observe(element);
  });
}

// Initialize animations when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  handleRevealAnimations();
});

// Parallax effect for the hero section
function parallaxHero() {
  const heroSection = document.querySelector(".hero");
  const heroImage = document.querySelector(".hero-image");

  window.addEventListener("scroll", () => {
    const scrollPosition = window.pageYOffset;

    if (scrollPosition <= heroSection.offsetHeight) {
      const parallaxValue = scrollPosition * 0.4;
      heroImage.style.transform = `translateY(${parallaxValue}px)`;
    }
  });
}

// Initialize parallax effect
parallaxHero();

// Add hover effects for feature cards
function addFeatureCardEffects() {
  const featureCards = document.querySelectorAll(".feature-card");

  featureCards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      const image = card.querySelector(".feature-image img");
      const glow = card.querySelector(".image-glow");

      if (image && glow) {
        image.style.transform = "scale(1.05)";
        glow.style.opacity = "0.3";
      }
    });

    card.addEventListener("mouseleave", () => {
      const image = card.querySelector(".feature-image img");
      const glow = card.querySelector(".image-glow");

      if (image && glow) {
        image.style.transform = "scale(1)";
        glow.style.opacity = "0.15";
      }
    });
  });
}

// Initialize feature card effects
addFeatureCardEffects();

// Add animated counter for statistics (can be added later)
function animateCounters() {
  const counters = document.querySelectorAll(".counter");
  const speed = 200; // Speed of counting animation

  counters.forEach((counter) => {
    const target = +counter.getAttribute("data-target");
    const increment = target / speed;

    const updateCounter = () => {
      const count = +counter.innerText;

      if (count < target) {
        counter.innerText = Math.ceil(count + increment);
        setTimeout(updateCounter, 1);
      } else {
        counter.innerText = target;
      }
    };

    updateCounter();
  });
}

// Dynamic text typing effect for headers (can be implemented later)
function typeWriterEffect(element, text, speed = 50) {
  let i = 0;
  element.innerHTML = "";

  function type() {
    if (i < text.length) {
      element.innerHTML += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }

  type();
}

// Add subtle particle effect to hero section (for future enhancement)
function createParticleEffect() {
  const canvas = document.createElement("canvas");
  const heroSection = document.querySelector(".hero");

  canvas.classList.add("particle-canvas");
  canvas.style.position = "absolute";
  canvas.style.top = "0";
  canvas.style.left = "0";
  canvas.style.width = "100%";
  canvas.style.height = "100%";
  canvas.style.pointerEvents = "none";
  canvas.style.zIndex = "0";

  heroSection.appendChild(canvas);

  // Canvas setup and particle animation can be implemented here
}
