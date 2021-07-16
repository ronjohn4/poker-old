document.querySelector('.add-game').addEventListener('click', addGame);
document.querySelector('.delete-game').addEventListener('click', deleteGame);


// add a Game to the db and display list and also display the result in the message list
function addGame(e) {
  // console.log('addGame() start');

  var gamelist = document.querySelector('.games').innerHTML;
  // console.log('gamelist:' + gamelist);

  const game = document.getElementById('game').value;
  // console.log(game);

  const xhr = new XMLHttpRequest();

  xhr.open('PUT', `/addgame/${game}`, true);

  xhr.onload = function() {
    if(this.status === 200) {
      // const response = JSON.parse(this.responseText);
      // console.log(response);
      
      // TODO - Update Game list (or insert new game at top of list) if game added
      if(response.type === 'success') {
          gamelist = `<tr><td><a href="/view/37">r6</a>${game}</td><td>mm/dd/yyyy</td></tr>` + gamelist;
      }

      document.querySelector('.games').innerHTML = gamelist;

      // TODO - add Game Added message to message list
    }
  }
  
  xhr.send(game);
  e.preventDefault();
}


// delete the Game from the db and display list and also display the result in the message list
function deleteGame(e) {
  // console.log('deleteGame() start');

  var gamelist = document.querySelector('.games').innerHTML;
  // console.log('gamelist:' + gamelist);

  const game = document.getElementById('game').value;
  // console.log(game);

  const xhr = new XMLHttpRequest();

  xhr.open('PUT', `/addgame/${game}`, true);

  xhr.onload = function() {
    if(this.status === 200) {
      // const response = JSON.parse(this.responseText);
      // console.log(response);
      
      // TODO - Update Game list (or insert new game at top of list) if game added
      if(response.type === 'success') {
          gamelist = `<tr><td><a href="/view/37">r6</a>${game}</td><td>mm/dd/yyyy</td></tr>` + gamelist;
      }

      document.querySelector('.games').innerHTML = gamelist;

      // TODO - add Game Added message to message list
    }
  }
  
  xhr.send(game);
  e.preventDefault();
}
