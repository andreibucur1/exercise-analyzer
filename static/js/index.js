
const registerUsername = localStorage.getItem('registerUsername');
const loginUsername = localStorage.getItem('loginUsername');


document.addEventListener("DOMContentLoaded", function () {

    let username = registerUsername || loginUsername;
    document.getElementById("usernameContent").innerText = username;
});

  function toggleDropdown() {
    const menu = document.getElementById("dropdownMenu");
    menu.classList.toggle("show");
  }

  function toggleEditSubmenu() {
    const submenu = document.getElementById("editSubmenu");
    submenu.style.display = submenu.style.display === "block" ? "none" : "block";
  }

  window.onclick = function(e) {
    if (!e.target.matches('.dropdown-btn')) {
      const dropdowns = document.getElementsByClassName("dropdown-content");
      for (let i = 0; i < dropdowns.length; i++) {
        dropdowns[i].classList.remove('show');
      }
    }
  }