/* Shared Admin Sidebar Logic */
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
