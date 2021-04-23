const URL_USERS = "http://127.0.0.1:8000/abonnements/fetch/users/"

/**
* Asynchronous function that fetches a list of user_follows from an url
* @param {string} url : the url to fecth
* @return : an await response as a JSON object
* */
async function fetchUsers(url) {
  try {
    let response = await fetch(url);
    return await response.json();
    //return await response.text();
  } catch (error) {
    console.log(error);
  }
}

async function renderUsers() {
/*
* asynchronous function to render the best movie into the html page
*/
  let parsed_data = await fetchUsers(URL_USERS);
  const input = document.getElementById('search_user')
  const form = document.getElementById('user_follows')
  form.elements["followed_user_id"].value = ""
  let error = document.querySelector('.error')
  let filteredArr = []

  input.addEventListener('keyup', (event) => {
    search_user_box.style.display = "block"
    search_user_box.innerHTML = ""
    filteredArr = parsed_data.filter(user => user['username'].startsWith(event.target.value))
    if (filteredArr.length > 1) {
      filteredArr.map(user => {
        search_user_box.innerHTML += `<div id="${user['id']}" class="search_user_item">${user['username']}</div>`
      })
    } else if (filteredArr.length == 1) {
        filteredArr.map(user => {
          search_user_box.innerHTML += `<div id="${user['id']}" class="search_user_item">${user['username']}</div>`
          input.value = user['username']
          form.elements["followed_user_id"].value = user['id']
        })
    } else {
        search_user_box.innerHTML = 'Aucun utilisateur trouvé'
    }
  });

  input.addEventListener('focus', (event) => {
    search_user_box.style.display = "block"
  });
  input.addEventListener('blur', (event) => {
    search_user_box.style.display = "none"
  });

  form.addEventListener("submit", function (event) {
    // Chaque fois que l'utilisateur tente d'envoyer les données
    // on vérifie que le champ followed_user_id est valide.
    if (form.elements["followed_user_id"].value == "") {

      // S'il est invalide, on affiche un message d'erreur personnalisé
      let followed_user = parsed_data.filter(user => user['username'] == input.value)[0]
      form.elements["followed_user_id"].value = followed_user['id']
    }
  }, false);
}

renderUsers();
