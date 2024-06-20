Telegram.WebApp.ready();
Telegram.WebApp.expand();

const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id');
const username = urlParams.get('username');

window.userId = userId;
window.username = username;

if (!userId || !username) {
    console.error('User ID or username is missing from URL parameters.');
    alert('User ID or username is missing from URL parameters.');
}

const menu = document.getElementById('menu');
const playButton = document.getElementById('playButton');
const totalScoreElement = document.getElementById('totalScore');
const totalScoreNumber = document.getElementById('score_total');

function fetchTotalScore() {
    const userId = window.userId;  // Используем значение из URL
    const url = `http://localhost:5000/get_total_score/${userId}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            totalScoreNumber.textContent = data.total_score;
        })
        .catch(error => console.error('Error:', error));
}


function fetchReferralsCount() {
    const userId = window.userId;
    const url = `http://localhost:5000/get_referrals_count/${userId}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            friendsNumber.textContent = data.referrals_count;
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    fetchTotalScore();
    fetchReferralsCount();
});

playButton.addEventListener('click', () => {
    menu.style.display = 'none';
    document.getElementById('gameContainer').style.display = 'block';
    loadScript('game.js');
});

function loadScript(src) {
    const script = document.createElement('script');
    script.src = src;
    script.onload = () => console.log(`${src} loaded`);
    document.head.appendChild(script);
}
