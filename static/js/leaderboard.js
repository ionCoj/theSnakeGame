async function fetchLeaderboard() 
{
  fetch('/getusersscores', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
.then(response => {
  if(response.status === 200)
  {
    console.log("Scores fetched successfully");
    return response.json()
  }
  else{
      console.log("Error fetching score");
    }
  })
  .then(data =>
  {
    displayLeaderboard(data);
  });
}
function displayLeaderboard(data) {
    const listElement = document.getElementById('leaderboard-list');
    listElement.innerHTML = '';
    listElement.innerHTML = data.map(entry => 
        `<li>${entry.player} - ${entry.score}</li>`
    ).join('');
}
document.addEventListener('DOMContentLoaded', fetchLeaderboard);

