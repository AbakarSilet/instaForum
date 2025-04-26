function getSystemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  
  function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  applyTheme(newTheme, true);
  }
  
  function applyTheme(theme, isManualChange = false) {
  document.documentElement.setAttribute("data-theme", theme);
  if (isManualChange) localStorage.setItem("userTheme", theme);
  
  // Mise à jour de l'icône Remix Icons
  const themeIcon = document.getElementById("theme-icon");
  if (theme === "dark") {
  themeIcon.classList.remove("ri-sun-line");
  themeIcon.classList.add("ri-moon-line");
  } else {
  themeIcon.classList.remove("ri-moon-line");
  themeIcon.classList.add("ri-sun-line");
  }
  }
  
  function loadTheme() {
  const userTheme = localStorage.getItem("userTheme");
  applyTheme(userTheme || getSystemTheme());
  
  // Écouteur pour les changements système (si pas de préférence utilisateur)
  if (!userTheme) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
  applyTheme(e.matches ? 'dark' : 'light');
  });
  }
  }
  
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
  