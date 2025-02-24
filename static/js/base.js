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
  