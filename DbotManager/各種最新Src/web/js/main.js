// Handle header scroll effect
const header = document.querySelector("header");
const scrollThreshold = 50;

window.addEventListener("scroll", () => {
  if (window.scrollY > scrollThreshold) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }
});

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();

    const targetId = this.getAttribute("href");
    const targetElement = document.querySelector(targetId);

    if (targetElement) {
      window.scrollTo({
        top: targetElement.offsetTop - 80, // Offset for header height
        behavior: "smooth",
      });
    }
  });
});

// Mobile navigation toggle (for smaller screens)
function createMobileNav() {
  const header = document.querySelector("header");
  const nav = document.querySelector("nav");

  // Create mobile menu button
  const mobileMenuBtn = document.createElement("button");
  mobileMenuBtn.classList.add("mobile-menu-btn");
  mobileMenuBtn.innerHTML = `
    <span class="bar"></span>
    <span class="bar"></span>
    <span class="bar"></span>
  `;

  // Check if we need to add mobile navigation
  function checkMobileNav() {
    if (window.innerWidth <= 768) {
      if (!document.querySelector(".mobile-menu-btn")) {
        header.appendChild(mobileMenuBtn);
        nav.classList.add("mobile-nav");
      }
    } else {
      if (document.querySelector(".mobile-menu-btn")) {
        document.querySelector(".mobile-menu-btn").remove();
        nav.classList.remove("mobile-nav");
        nav.classList.remove("active");
      }
    }
  }

  // Toggle mobile menu
  mobileMenuBtn.addEventListener("click", () => {
    nav.classList.toggle("active");
    mobileMenuBtn.classList.toggle("active");
  });

  // Close mobile menu when clicking on a link
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (nav.classList.contains("active")) {
        nav.classList.remove("active");
        mobileMenuBtn.classList.remove("active");
      }
    });
  });

  // Initial check and add event listener for window resize
  checkMobileNav();
  window.addEventListener("resize", checkMobileNav);
}

// Initialize mobile navigation
createMobileNav();

// Add CSS for mobile navigation
function addMobileNavStyles() {
  const style = document.createElement("style");
  style.textContent = `
    .mobile-menu-btn {
      display: none;
      background: none;
      border: none;
      cursor: pointer;
      padding: 10px;
      z-index: 1001;
    }

    .mobile-menu-btn .bar {
      display: block;
      width: 25px;
      height: 3px;
      margin: 5px auto;
      background-color: var(--text-white);
      transition: all 0.3s ease-in-out;
    }

    .mobile-menu-btn.active .bar:nth-child(1) {
      transform: translateY(8px) rotate(45deg);
    }

    .mobile-menu-btn.active .bar:nth-child(2) {
      opacity: 0;
    }

    .mobile-menu-btn.active .bar:nth-child(3) {
      transform: translateY(-8px) rotate(-45deg);
    }

    @media screen and (max-width: 768px) {
      .mobile-menu-btn {
        display: block;
      }

      .mobile-nav {
        position: fixed;
        top: 0;
        right: -100%;
        width: 70%;
        height: 100vh;
        background-color: var(--navy-medium);
        padding-top: 80px;
        transition: right 0.3s ease;
        z-index: 1000;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        align-items: center;
      }

      .mobile-nav.active {
        right: 0;
      }

      .mobile-nav ul {
        flex-direction: column;
        width: 100%;
        padding: 0 20px;
      }

      .mobile-nav ul li {
        margin: 15px 0;
        width: 100%;
        text-align: center;
      }
    }
  `;

  document.head.appendChild(style);
}

// Add mobile navigation styles
addMobileNavStyles();

// Feature cards hover effects
document.addEventListener("DOMContentLoaded", function () {
  const featureCards = document.querySelectorAll(".feature-card");

  featureCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      // Add subtle glow effect on hover
      this.style.boxShadow = "0 25px 70px rgba(212, 175, 55, 0.15)";
    });

    card.addEventListener("mouseleave", function () {
      // Reset to default shadow
      this.style.boxShadow = "";
    });
  });
});
