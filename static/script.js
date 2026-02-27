// --- 1. Responsive Navbar Toggle ---
function toggleMenu() {
  const navLinks = document.getElementById("navLinks");
  navLinks.classList.toggle("active");
}

document.addEventListener("click", function (event) {
  const navLinks = document.getElementById("navLinks");
  const hamburger = document.querySelector(".hamburger");

  if (navLinks.classList.contains("active")) {
    if (!navLinks.contains(event.target) && !hamburger.contains(event.target)) {
      navLinks.classList.remove("active");
    }
  }
});

// --- 2. Toggle Password Visibility ---
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

// --- 3. Auto-Hide Toasts ---
window.onload = function () {
  const toasts = document.getElementsByClassName("toast");
  if (toasts.length > 0) {
    setTimeout(function () {
      for (let toast of toasts) {
        toast.style.transition = "opacity 0.5s ease";
        toast.style.opacity = "0";

        setTimeout(() => (toast.style.display = "none"), 500);
      }
    }, 4000);
  }
};

// --- 4. Back to Top Button ---
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

// --- 5. Modal for Student ID Details ---
function openModal(card) {
  const modalTitle = document.getElementById("modalTitle");
  const modalImg = document.getElementById("modalImg");
  const modalDetails = document.getElementById("modalDetails");

  const type = card.getAttribute("data-type");
  const imgStr = card.getAttribute("data-img");
  const dateStr = card.getAttribute("data-date");
  const itemId = card.getAttribute("data-id");

  modalImg.src = imgStr;

  let htmlContent = "";

  if (type === "Lost") {
    modalTitle.innerText = "Lost Item Details";
    const name = card.getAttribute("data-name");
    const reg = card.getAttribute("data-reg");
    const dept = card.getAttribute("data-dept");

    htmlContent = `
            <div class="detail-row"><strong>Student:</strong> ${name}</div>
            <div class="detail-row"><strong>Reg No:</strong> ${reg}</div>
            <div class="detail-row"><strong>Department:</strong> ${dept}</div>
            <div class="detail-row"><strong>Reported:</strong> ${dateStr}</div>
            <p style="margin-top:15px; color:#666; font-size:0.9rem;">
               If you find this ID, please report it via the 'Report Found' page.
            </p>
        `;
  } else {
    modalTitle.innerText = "Found Item Details";
    const loc = card.getAttribute("data-loc");

    htmlContent = `
            <div class="detail-row"><strong>Found At:</strong> ${loc}</div>
            <div class="detail-row"><strong>Reported:</strong> ${dateStr}</div>
            <hr style="margin: 15px 0; border: 0; border-top: 1px solid #eee;">
        `;

    if (typeof userLoggedIn !== "undefined" && userLoggedIn) {
      htmlContent += `
                <p style="margin-bottom: 10px; font-weight: bold; color: #2c3e50;">Is this your ID?</p>
                <form action="/claim/${itemId}" method="POST">
                    <button type="submit" class="claim-btn">✋ Claim This ID</button>
                </form>
            `;
    } else {
      htmlContent += `
                <p style="color: #1d52a1ff;">
                    Is this your ID? <br>
                    <a href="/login" style="color: #1d52a1ff; font-weight: bold; text-decoration: underline;">
                        Login to claim it.
                    </a>
                </p>
            `;
    }
  }

  modalDetails.innerHTML = htmlContent;

  openModalById("idModal");
}

function closeModal() {
  closeModalById("idModal");
}

// --- 6. UNIVERSAL MODAL HANDLING ---
// Open any modal by passing its ID
function openModalById(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "flex";
  }
}

// Close any modal by passing its ID
function closeModalById(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = "none";
  }
}

// Click outside to close modal
window.onclick = function (event) {
  if (
    event.target.classList.contains("modal") ||
    event.target.classList.contains("modal-overlay")
  ) {
    event.target.style.display = "none";
  }
};

// --- 7. Client-Side Search / Filter Logic ---
function filterGrid() {
  const input = document.getElementById("searchInput");
  const filter = input.value.toLowerCase();

  const grid = document.getElementById("itemsGrid");
  const cards = grid.getElementsByClassName("card");

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];

    const name = card.getAttribute("data-name") || "";
    const reg = card.getAttribute("data-reg") || "";
    const dept = card.getAttribute("data-dept") || "";
    const loc = card.getAttribute("data-loc") || "";

    const combinedText = (
      name +
      " " +
      reg +
      " " +
      dept +
      " " +
      loc
    ).toLowerCase();

    if (combinedText.indexOf(filter) > -1) {
      card.style.display = "";
    } else {
      card.style.display = "none";
    }
  }
}
