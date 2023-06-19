/* eslint-disable */
export function darkModeToggle() {
  let theme = "light";
  if (document.documentElement.getAttribute('data-bs-theme') === "light") {
      theme = "dark";
  }
  const toggleButton = document.getElementById("darkModeToggleButton");
  if (theme === "light") {
    toggleButton.innerText = "Dark";
    toggleButton.classList.add('btn-dark');
    toggleButton.classList.remove('btn-light');
  } else {
    toggleButton.innerText = "Light";
    toggleButton.classList.add('btn-light');
    toggleButton.classList.remove('btn-dark');
  }
  document.documentElement.setAttribute('data-bs-theme', theme)
  localStorage.setItem("theme", theme);
};

export function main() {
  const currentTheme = localStorage.getItem("theme");
  document.documentElement.setAttribute('data-bs-theme', currentTheme)
  const toggleButton = document.getElementById("darkModeToggleButton");
  if (currentTheme === "light") {
    toggleButton.innerText = "Dark";
    toggleButton.classList.add('btn-dark');
    toggleButton.classList.remove('btn-light');
  } else {
    toggleButton.innerText = "Light";
    toggleButton.classList.add('btn-light');
    toggleButton.classList.remove('btn-dark');

  }
}
