
const registerUsername = localStorage.getItem('registerUsername');
const loginUsername = localStorage.getItem('loginUsername');


document.addEventListener("DOMContentLoaded", function () {

    let username = registerUsername || loginUsername;
    document.getElementById("usernameContent").innerText = username;
});

function toggleDropdown() {
    document.getElementById("dropdownMenu").classList.toggle("show");
  }

  // Închide dropdown-ul dacă se face click în afara lui
  window.onclick = function(e) {
    if (!e.target.matches('.dropdown-btn')) {
      const dropdowns = document.getElementsByClassName("dropdown-content");
      for (let i = 0; i < dropdowns.length; i++) {
        dropdowns[i].classList.remove('show');
      }
    }
  }