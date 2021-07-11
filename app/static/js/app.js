// document.querySelector('.get-jokes').addEventListener('click', getJokes);
document.querySelector('.add-game').addEventListener('click', getJokes);

// test comment

function getJokes(e) {
  console.log('getJokes() 2');


  var gamelist = document.querySelector('.games').innerHTML;
  // console.log('gamelist:' + gamelist);

  const game = document.getElementById('game').value;
  // var url = window.location.host;

  // console.log(url);

  // url = url.concat(`/addgame/${game}`);

  // console.log(game);
  // console.log(url);

  const xhr = new XMLHttpRequest();

  xhr.open('PUT', `/addgame/${game}`, true);

  xhr.onload = function() {
    if(this.status === 200) {
      // const response = JSON.parse(this.responseText);

      // console.log(response);
      
      // let output = '';

      if(response.type === 'success') {
      //   response.value.forEach(function(joke){
          gamelist = `<tr><td><a href="/view/37">r6</a>      ${game}</td><td>mm/dd/yyyy</td></tr>` + gamelist;
      //   });
      // } else {
      //   output += '<li>Something went wrong</li>';
      }

      // document.querySelector('.jokes').innerHTML = output;
      document.querySelector('.games').innerHTML = gamelist;
      // console.log(output);
      // alert('Game added');
    }
  }

  
  xhr.send(game);

  e.preventDefault();
}
