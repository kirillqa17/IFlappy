Telegram.WebApp.ready();
Telegram.WebApp.expand();

const menu = document.getElementById('menu');
const playButton = document.getElementById('playButton');
const totalScoreElement = document.getElementById('totalScore');

function fetchTotalScore() {
    const userId = window.userId;  // Используем значение из URL
    const url = `http://localhost:5000/get_total_score/${userId}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            totalScoreElement.textContent = `Total счет: ${data.total_score}`;
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', fetchTotalScore);

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
