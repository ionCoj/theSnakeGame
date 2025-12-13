async function fetchLeaderboard() {
  const response = await fetch('/leaderboard1');
  const data = await response.json();
  console.log(data);
  displayLeaderboard(data);
}
function displayLeaderboard(data) {
    const listElement = document.getElementById('leaderboard-list');
    listElement.innerHTML = '';
    listElement.innerHTML = data.map(entry => 
        `<li>${entry.player} - ${entry.score}</li>`
    ).join('');
}
document.addEventListener('DOMContentLoaded', fetchLeaderboard);

