// --- 1. Toggle Password Visibility ---
function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);

  if (input.type === "password") {
    input.type = "text";
    icon.textContent = "❌";
  } else {
    input.type = "password";
    icon.textContent = "👁️";
  }
}

// --- 2. Shared Admin Sidebar Logic ---
function toggleSidebar() {
  const sidebar = document.getElementById("adminSidebar");
  const overlay = document.querySelector(".sidebar-overlay");

  sidebar.classList.toggle("active");

  if (sidebar.classList.contains("active")) {
    overlay.style.display = "block";
  } else {
    overlay.style.display = "none";
  }
}

// --- 3. Back to Top Button ---
const backToTopBtn = document.getElementById("backToTop");

window.onscroll = function () {
  scrollFunction();
};

function scrollFunction() {
  if (
    document.body.scrollTop > 300 ||
    document.documentElement.scrollTop > 300
  ) {
    backToTopBtn.style.display = "block";
  } else {
    backToTopBtn.style.display = "none";
  }
}

if (backToTopBtn) {
  backToTopBtn.addEventListener("click", function () {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
}
