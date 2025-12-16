// --- 1. Responsive Navbar Toggle ---
function toggleMenu() {
  const navLinks = document.getElementById("navLinks");
  navLinks.classList.toggle("active");
}

// --- 2. Modal for Student ID Details ---
function openModal(cardElement) {
  const modal = document.getElementById("idModal");
  const modalImg = document.getElementById("modalImg");
  const modalDetails = document.getElementById("modalDetails");
  const modalTitle = document.getElementById("modalTitle");

  const type = cardElement.getAttribute("data-type");
  const imgUrl = cardElement.getAttribute("data-img");
  const date = cardElement.getAttribute("data-date");

  modalImg.src = imgUrl;

  if (type === "Lost") {
    const name = cardElement.getAttribute("data-name");
    const reg = cardElement.getAttribute("data-reg");
    const dept = cardElement.getAttribute("data-dept");

    modalTitle.innerText = "Lost Student ID";
    modalDetails.innerHTML = `
            <p><strong>Student Name:</strong> ${name}</p>
            <p><strong>Reg Number:</strong> ${reg}</p>
            <p><strong>Department:</strong> ${dept}</p>
            <p><strong>Date Reported:</strong> ${date}</p>
            <hr>
            <p style="color:red; font-size:0.9rem;">
                <em>If found, please report it using the "Report Found ID" page.</em>
            </p>
        `;
  } else {
    const loc = cardElement.getAttribute("data-loc");

    modalTitle.innerText = "Found Student ID";
    modalDetails.innerHTML = `
            <p><strong>Location Found:</strong> ${loc}</p>
            <p><strong>Date Reported:</strong> ${date}</p>
            <hr>
            <p style="color:green; font-weight:bold;">
                Is this your ID? Please visit the security office to claim it.
            </p>
        `;
  }

  modal.style.display = "flex";
}

function closeModal() {
  document.getElementById("idModal").style.display = "none";
}

// Close modal if user clicks outside the box
window.onclick = function (event) {
  const modal = document.getElementById("idModal");
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// --- 3. Client-Side Search / Filter Logic ---
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
