const API_BASE_URL = 'http://127.0.0.1:8080';
async function fetchLeaderboard() {
  const response = await fetch(`${API_BASE_URL}/leaderboard`);
  const data = await response.json();
  console.log(data);
  //return data;
  displayLeaderboard(data);
  println(data);
}
function displayLeaderboard(data) {
    const listElement = document.getElementById('leaderboard-list');
    listElement.innerHTML = '';
    listElement.innerHTML = data.map(entry => 
        `<li>${entry.player} - ${entry.score}</li>`
    ).join('');
}
document.addEventListener('DOMContentLoaded', fetchLeaderboard);