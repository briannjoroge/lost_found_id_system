// --- 1. Shared Admin Sidebar Logic ---
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

// --- 2. Back to Top Button ---
const backToTopBtn = document.getElementById("backToTop");

window.onscroll = function () {
  scrollFunction();
};

function scrollFunction() {
  if (
    document.body.scrollTop > 200 ||
    document.documentElement.scrollTop > 200
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
