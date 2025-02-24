
// Fonction pour basculer entre le thème clair et le thème sombre
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);

    // Change the icon and its color based on the theme
    const themeIcon = document.getElementById("theme-icon");
    if (newTheme === "dark") {
        themeIcon.classList.remove("fa-sun");
        themeIcon.classList.add("fa-moon");
        themeIcon.style.color = "#ffffff"; // Change icon color for dark theme
    } else {
        themeIcon.classList.remove("fa-moon");
        themeIcon.classList.add("fa-sun");
        themeIcon.style.color = "#000000"; // Change icon color for light theme
    }
}

// Fonction pour maintenir le thème sélectionné par l'utilisateur entre les sessions
function loadTheme() {
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);

    // Set the icon and its color based on the saved theme
    const themeIcon = document.getElementById("theme-icon");
    if (savedTheme === "dark") {
        themeIcon.classList.remove("fa-sun");
        themeIcon.classList.add("fa-moon");
        themeIcon.style.color = "#ffffff"; // Change icon color for dark theme
    } else {
        themeIcon.classList.remove("fa-moon");
        themeIcon.classList.add("fa-sun");
        themeIcon.style.color = "#000000"; // Change icon color for light theme
    }
}
// Fonction pour basculer l'affichage de la barre latérale
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("active");
    if (sidebar.classList.contains("active")) {
        sidebar.style.left = "0";
    } else {
        sidebar.style.left = "-250px";
    }
}

// Fonction pour afficher/masquer les sous-menus dans la barre latérale
function toggleDropdown(event) {
    event.preventDefault();
    const dropdown = event.target.closest('.dropdown');
    dropdown.classList.toggle("active");
}

// Appel de la fonction pour charger le thème dès que la page se charge
window.addEventListener("DOMContentLoaded", loadTheme);


