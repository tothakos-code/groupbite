function saveUsername() {
  let user = document.getElementById("username-input").value;
  if (user !== "") {
    document.cookie = `username=${encodeURIComponent(user)}; expires=${getCookieExpirationDate(365)}`;
    username = user;
    closePopup();
    displayUsername(username);
  }
}

function transferBasketToFalusi() {
  let psid = document.getElementById("psid-input").value;
  if (psid !== "") {
    closePSIDPopup();
    fetch(`http://${window.location.hostname}/api/transferBasket`,{
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ psid: psid })
    })
      .then(response => {
        console.log(response.statusText);
        if (response.statusText == "OK") {
          openOrderEndPopup();
        } else {
          alert("Valami hiba történt.");
        }
      })
        .catch(error => console.error(error))
  }
}

function orderPayed() {
  socket.emit("Ordered and Payed");
  closeOrderEndPopup();
}

function openOrderEndPopup(){
  let popup = document.getElementById("orderend-popup");
  popup.style.display = "block";
}

function closeOrderEndPopup(){
  let popup = document.getElementById("orderend-popup");
  popup.style.display = "none";
}

function displayUsername(username) {
  let usernameDisplay = document.getElementById("username-display");
  usernameDisplay.innerHTML = "Hello, " + username + "!";
  usernameDisplay.style.display = "block";
}

function closePopup() {
  if (username !== null) {
    let popup = document.getElementById("popup");
    popup.style.display = "none";
  }
}

function openPopup() {
  let popup = document.getElementById("popup");
  popup.style.display = "block";
}

function closePSIDPopup() {
  if (username !== "" || username === null) {
    let popup = document.getElementById("psid-popup");
    popup.style.display = "none";
  }
}

function openPSIDPopup() {
  let popup = document.getElementById("psid-popup");
  popup.style.display = "block";
}

function getUsernameFromCookie() {
  let cookies = document.cookie.split(';');
  for (let i = 0; i < cookies.length; i++) {
    let cookie = cookies[i].trim();
    if (cookie.startsWith("username=")) {
      return decodeURIComponent(cookie.substring("username=".length));
    }
  }
  return null;
}

function getBasketFromCookies() {
 const basketString = document.cookie.replace(/(?:(?:^|.*;\s*)basket\s*\=\s*([^;]*).*$)|^.*$/, '$1');
 return basketString ? JSON.parse(basketString) : null;
}

function setBasketInCookies(basket) {
  if ( orderState === 'order') {
    alert("Figyelem! A rendelő elkezdte áthelyezni a falusiba a kosarat és lehet, hogy nem veszi észre, hogy te változtattál a kosaradon. Jelezd neki mielött nem késő!")
  }
  if ( orderState === 'closed') {
    alert("A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.")
    return
  }

  const basketString = JSON.stringify(basket);
  var now = new Date();
  var time = now.getTime();
  time += 3600 * 1000 * 16;
  now.setTime(time);
  document.cookie = `basket=${basketString}; path=/; expires=${now.toUTCString()}`;
}

function clearBasket() {
  if ( orderState === 'order') {
    alert("Figyelem! A rendelő elkezdte áthelyezni a falusiba a kosarat és lehet, hogy nem veszi észre, hogy te változtattál a kosaradon. Jelezd neki mielött nem késő!")
  }
  if ( orderState === 'closed') {
    alert("A rendelés már el lett küldve. Már nem módosíthatod a kosaradat.")
    return
  }
  // Remove the basket cookie
  document.cookie = 'basket=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC';
  updateBasketList();
}


function getCookieExpirationDate(days) {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  return date.toUTCString();
}

function updateBasketList() {
  const basketList = document.getElementById('basketList');
  const localvalue = document.getElementById("localbasket-value");

  // Clear the current list
  basketList.innerHTML = '';
  const localBasket = getBasketFromCookies() || {};
  socket.emit("Server Basket Update", { [username]: localBasket });
  if (!localBasket) {
    localvalue.innerText = "0 Ft"
    return;
  }

  let localBasketValue = 0;
  // Loop through the basket items and add them to the list
  Object.entries(localBasket).forEach(([itemSizeKey, item]) => {
  // for (let item of basketItems) {
    const listItem = document.createElement('li');
    const deleteButton = document.createElement('button');
    const quantitySpan = document.createElement('span');
    deleteButton.innerText = 'Töröl';
    deleteButton.classList.add("btn");
    deleteButton.classList.add("btn-secondary");

    // Add an event listener to the delete button to remove the item from the basket
    deleteButton.addEventListener('click', () => {
      const basketItem = item;
      if (basketItem.quantity == 1) {
        // Otherwise, remove the entry from the basket
        delete localBasket[itemSizeKey]
      } else {
        // If the item already exists in the basket, decrement the quantity
        basketItem.quantity -= 1;
      }
      setBasketInCookies(localBasket);

      updateBasketList();
    });
    localBasketValue += Number(item.quantity) * Number(item.price.split(' ')[0])
    quantitySpan.innerText = `${item.quantity} x `;
    listItem.innerText = `${item.name} (${item.size}) - ${item.price}`;
    listItem.insertBefore(quantitySpan, listItem.firstChild);
    listItem.appendChild(deleteButton);
    basketList.appendChild(listItem);
  });

  localvalue.innerText = localBasketValue + " Ft + Szállítás díj szétosztva"

}

function updateGlobalBasketList(globalBasket) {
  const globalbasketList = document.getElementById('globalbasketList');
  // Clear the current list
  globalbasketList.innerHTML = '';

  if (!globalBasket) {
    return;
  }

  let globalBasketValue = 0;
  let boxcount = 0;

  let traransportFee = 400;
  let transportFeePerPerson = Math.ceil(traransportFee / Object.keys(globalBasket).length);

  // Loop through the basket items and add them to the list
  Object.entries(globalBasket).forEach(([person, basket]) => {
    if (!basket || Object.entries(basket).length === 0) {
      return;
    }
    const personItem = document.createElement('ul');
    personItem.classList.add("list");
    const headerItem = document.createElement('li');
    const usernameItem = document.createElement('span');
    usernameItem.innerText = person;
    const userPriceSumItem = document.createElement('span');
    userPriceSumItem.classList.add("text-end")
    const basketItem = document.createElement('li');

    const userBasketItem = document.createElement('ul');
    userBasketItem.classList.add("list");
    var priceSum = 0;
    Object.entries(basket).forEach(([id, item]) => {
      const listItem = document.createElement('li');
      const quantitySpan = document.createElement('span');
      const nameSpan = document.createElement('span');
      nameSpan.classList.add("text-end")
      let currentItemPriceSum = Number(item.quantity) * Number((item.price).split(' ')[0]);
      priceSum += currentItemPriceSum;
      boxcount += item.quantity;
      userPriceSumItem.title = userPriceSumItem.title + currentItemPriceSum + " Ft + ";
      quantitySpan.innerText = `${item.quantity} x `;
      nameSpan.innerText = `${item.name} (${item.size}) - ${item.price}`;
      listItem.appendChild(quantitySpan);
      listItem.appendChild(nameSpan);
      userBasketItem.appendChild(listItem);
    });
    userPriceSumItem.title = userPriceSumItem.title + transportFeePerPerson + ' Ft(szállítás) = ' + (priceSum + transportFeePerPerson) + ' Ft';
    userPriceSumItem.innerText = (priceSum + transportFeePerPerson) + ' Ft';

    globalBasketValue += priceSum;
    headerItem.insertBefore(usernameItem, personItem.firstChild);
    headerItem.appendChild(userPriceSumItem);
    basketItem.appendChild(userBasketItem);
    personItem.appendChild(headerItem);
    personItem.appendChild(basketItem);
    if (person === username) {
      globalbasketList.prepend(personItem);
    } else {
      globalbasketList.append(personItem);
    }
  });
  const globalvalue = document.getElementById("globalbasket-value");
  globalvalue.innerText = (globalBasketValue + traransportFee) + " Ft"
  const boxcountItem = document.getElementById("globalbasket-boxcount");
  boxcountItem.innerText = boxcount + " db doboz"
}

function createListItem(item) {
  const listItemElementTemplate = document.getElementById("etlapListItemTemplate");
  const listItemElementClone = listItemElementTemplate.content.cloneNode(true);

  // Set the item name
  listItemElementClone.querySelector('span').innerText = item.label;

  // Add a button for each size
  item.sizes.forEach(size => {
    const temp = document.getElementById("etlapListItemButtonTemplate");
    const sizeButtonClone = temp.content.cloneNode(true);
    const sizeButton = sizeButtonClone.querySelector('button')
    sizeButton.innerText = size.label;

    // Add an event listener to update the basket and save it to cookies
    sizeButton.addEventListener('click', () => {
      const basket = getBasketFromCookies() || {};

      const itemSizeKey = `${item.id}-${size.size}`;
      if (basket[itemSizeKey]) {
        // If the item already exists in the basket, increment the quantity
        basket[itemSizeKey].quantity += 1;
      } else {
        // Otherwise, add a new entry to the basket
        basket[itemSizeKey] = {
          id: item.id,
          name: item.label,
          size: size.size,
          price: size.price,
          link: size.link,
          quantity: 1
        };
      }
      setBasketInCookies(basket);
      updateBasketList();
    });
    // Add the size button to the list element
    listItemElementClone.querySelector('div').appendChild(sizeButtonClone);
  });

  return listItemElementClone.querySelector('li');
}

let username = getUsernameFromCookie();
let socket;
let orderState;

function darkModeToggle() {
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

function main() {
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

  if (username !== null) {
    displayUsername(username);
  } else {
    openPopup();
  }

  $(document).ready(function(){
    // sending a connect request to the server.
    socket = io.connect();

    socket.emit('Request order state',function(state) {
      console.log("Recived data from return");
      orderState = state;
    });

    socket.on('connect', function() {
      console.log('Socket.IO connection established');
      updateBasketList();
    });

    socket.on('Order state changed', function(state) {
      console.log("Order update incoming");
      orderState = state;
    });

    socket.on('Clear Local Basket', function() {
      console.log('Clearing local basket as requested by the server');
      clearBasket()
    });

    socket.on('Client Basket Update', function(msg) {
      console.log('Global basket incomming via websocket: ', msg);
      updateGlobalBasketList(msg.basket);
    });

  });

  fetch(`http://${window.location.hostname}/api/getetlap`)
    .then(response => response.json())
      .then(data => {

        const listContainer = document.getElementById('foodList');

        data.forEach(item => {
          listContainer.appendChild(createListItem(item));
        });
        updateBasketList()

      })
    .catch(error => console.error(error));
}

main();
