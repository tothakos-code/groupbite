/* eslint-disable */
export function clearBasket() {
  if ( orderState === 'order') {
    alert("Figyelem! A rendelő elkezdte áthelyezni a falusiba a kosarat és lehet, hogy nem veszi észre, hogy te változtattál a kosaradon. Jelezd neki mielött nem késő!")
  }
  if ( orderState === 'closed') {
    alert("A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.")
    return
  }
  // Remove the basket cookie
  document.cookie = 'basket=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
  // updateBasketList();
}

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
