// Fonction pour détecter la préférence système
function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

// Fonction pour basculer entre le thème clair et le thème sombre
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  applyTheme(newTheme, true); // true indique un changement manuel
}

// Fonction pour appliquer le thème
function applyTheme(theme, isManualChange = false) {
  document.documentElement.setAttribute("data-theme", theme);
  
  // Si c'est un changement manuel, sauvegarder la préférence
  if (isManualChange) {
      localStorage.setItem("userTheme", theme);
  }

  // Mettre à jour l'icône
  const themeIcon = document.getElementById("theme-icon");
  if (theme === "dark") {
      themeIcon.classList.remove("fa-sun");
      themeIcon.classList.add("fa-moon");
      themeIcon.style.color = "#ffffff";
  } else {
      themeIcon.classList.remove("fa-moon");
      themeIcon.classList.add("fa-sun");
      themeIcon.style.color = "#000000";
  }
}

// Fonction pour charger le thème initial
function loadTheme() {
  const userTheme = localStorage.getItem("userTheme");
  
  if (userTheme) {
      // Si l'utilisateur a déjà choisi un thème, utiliser celui-là
      applyTheme(userTheme);
  } else {
      // Sinon, utiliser le thème système
      applyTheme(getSystemTheme());
      
      // Écouter les changements de thème système
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
          if (!localStorage.getItem("userTheme")) {
              applyTheme(e.matches ? 'dark' : 'light');
          }
      });
  }
}

// Appeler loadTheme au chargement de la page
document.addEventListener('DOMContentLoaded', loadTheme);


const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const content = document.getElementById('content');
const overlay = document.getElementById('overlay');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const mobileMenu = document.getElementById('mobileMenu');

// Fonction pour basculer le sidebar
sidebarToggle.addEventListener('click', () => {
  if (sidebar.style.left === '0px') {
    sidebar.style.left = '-300px'; // Mise à jour avec la nouvelle largeur
    content.style.marginLeft = '0px'; // Retirer la marge gauche du contenu
    if (window.innerWidth > 768) { // Vérifie si l'utilisateur n'est pas en mode mobile
      sidebarToggle.style.display = 'block';
    }
    overlay.style.display = 'none'; // Masquer l'overlay
  } else {
    sidebar.style.left = '0px';
    content.style.marginLeft = '300px'; // Mise à jour avec la nouvelle largeur
    sidebarToggle.style.display = 'none';
    overlay.style.display = 'block'; // Afficher l'overlay
  }
});

// Fonction pour fermer le sidebar en cliquant en dehors
overlay.addEventListener('click', () => {
  sidebar.style.left = '-300px'; // Mise à jour avec la nouvelle largeur
  content.style.marginLeft = '0px'; // Retirer la marge gauche du contenu
  if (window.innerWidth > 768) { // Vérifie si l'utilisateur n'est pas en mode mobile
    sidebarToggle.style.display = 'block';
  }
  overlay.style.display = 'none'; // Masquer l'overlay
});


// Fonction pour basculer le menu mobile
mobileMenuToggle.addEventListener('click', () => {
if (mobileMenu.style.display === 'none' || mobileMenu.style.display === '') {
  mobileMenu.style.display = 'flex'; // Afficher le menu mobile
  overlay.style.display = 'block'; // Afficher l'overlay
} else {
  mobileMenu.style.display = 'none'; // Masquer le menu mobile
  overlay.style.display = 'none'; // Masquer l'overlay
}
});

// Fonction pour fermer le menu mobile en cliquant en dehors
overlay.addEventListener('click', () => {
if (window.innerWidth <= 768) { // Vérifie si l'utilisateur est en mode mobile
  mobileMenu.style.display = 'none'; // Masquer le menu mobile
  overlay.style.display = 'none'; // Masquer l'overlay
}
});
