const canvas = document.getElementById('gameCanvas');
const context = canvas.getContext('2d');
const messageDiv = document.getElementById('message');
const restartButton = document.getElementById('restartButton');
const scoreBackground = document.getElementById('scoreBackground');
const scoreSpan = document.getElementById('score');

const birdImg = new Image();
const birdFlapImg = new Image();
const pipeNorthImg = new Image();
const pipeSouthImg = new Image();
const backgroundImg = new Image();
const smokeImg = new Image();

birdImg.src = 'images/sasha.jpg';
birdFlapImg.src = 'images/sasha_flap.jpg';
pipeNorthImg.src = 'images/chlen_vniz.jpg';
pipeSouthImg.src = 'images/chlen_vverh.jpg';
backgroundImg.src = 'images/fon.png';
smokeImg.src = 'images/smoke.png';

for (let img of [birdImg, birdFlapImg, pipeNorthImg, pipeSouthImg, backgroundImg, smokeImg]) {
    img.onerror = () => {
        console.error(`Failed to load image: ${img.src}`);
    };
}

const bird = {
    x: 50,
    y: 150,
    width: 44,
    height: 34,
    gravity: 0.25,
    lift: -5,
    velocity: 0
};

const pipes = [];
const smokes = [];
const pipeWidth = 150;
const gap = 200;

let frame = 0;
let score = 0;
let gameStarted = false;
let birdFlap = false;
let gameInterval;

const backgroundSpeed = 2;
let backgroundX = 0;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

function startGame() {
    gameStarted = true;
    frame = 0;
    score = 0;
    pipes.length = 0;
    smokes.length = 0;
    bird.y = 150;
    bird.velocity = 0;
    scoreBackground.style.display = 'block';
    gameInterval = setInterval(draw, 1000 / 60);
    menu.style.display = 'none';
    gameContainer.style.display = 'block';
}

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);

    backgroundX -= backgroundSpeed;
    if (backgroundX <= -canvas.width) {
        backgroundX = 0;
    }

    context.drawImage(backgroundImg, backgroundX, 0, canvas.width, canvas.height);
    context.drawImage(backgroundImg, backgroundX + canvas.width, 0, canvas.width, canvas.height);

    if (birdFlap) {
        context.drawImage(birdFlapImg, bird.x, bird.y, bird.width, bird.height);
    } else {
        context.drawImage(birdImg, bird.x, bird.y, bird.width, bird.height);
    }

    bird.velocity += bird.gravity;
    bird.y += bird.velocity;

    if (bird.y + bird.height > canvas.height || bird.y < 0) {
        triggerGameOver();
        return;
    }

    if (frame % 250 === 0) {
        let pipeY = Math.floor(Math.random() * (canvas.height - gap - pipeWidth)) - canvas.height;
        pipes.push({
            x: canvas.width,
            y: pipeY
        });
    }

    for (let i = 0; i < pipes.length; i++) {
        pipes[i].x -= 2;

        if (pipes[i].x + pipeWidth < 0) {
            pipes.splice(i, 1);
            score++;
            scoreSpan.textContent = score;
        }

        context.drawImage(pipeNorthImg, pipes[i].x, pipes[i].y, pipeWidth, canvas.height);
        context.drawImage(pipeSouthImg, pipes[i].x, pipes[i].y + canvas.height + gap, pipeWidth, canvas.height);

        if (
            bird.x + bird.width > pipes[i].x &&
            bird.x < pipes[i].x + pipeWidth &&
            (bird.y < pipes[i].y + canvas.height || bird.y + bird.height > pipes[i].y + canvas.height + gap)
        ) {
            triggerGameOver();
            return;
        }
    }

    for (let i = 0; i < smokes.length; i++) {
        context.globalAlpha = smokes[i].opacity;
        context.drawImage(smokeImg, smokes[i].x, smokes[i].y, 50, 50);
        smokes[i].y += smokes[i].vy;
        smokes[i].opacity -= 0.01;
        if (smokes[i].opacity <= 0) {
            smokes.splice(i, 1);
        }
    }
    context.globalAlpha = 1.0;

    frame++;
}

function triggerGameOver() {
    gameStarted = false;
    clearInterval(gameInterval);
    sendGameResult(score);
    setTimeout(gameOver, 1000);
}

function gameOver() {
    messageDiv.textContent = "Вы посадили Сашу на хуй.\nВаш счет: " + score;
    messageDiv.style.display = "block";
    restartButton.style.display = "block";
    scoreBackground.style.display = "none";
}

function resetGame() {
    bird.y = 150;
    bird.velocity = 0;
    pipes.length = 0;
    smokes.length = 0;
    score = 0;
    frame = 0;
    birdFlap = false;
    messageDiv.style.display = "none";
    restartButton.style.display = "none";
    startGame();
}

document.addEventListener('keydown', (event) => {
    if (event.code === 'Space' && gameStarted) {
        bird.velocity = bird.lift;
        birdFlap = true;
        setTimeout(() => birdFlap = false, 100);
        smokes.push({ x: bird.x, y: bird.y, vy: bird.velocity, opacity: 0.5 });
    }
});

restartButton.addEventListener('click', resetGame);

function sendGameResult(score) {
    const userId = Telegram.WebApp.initDataUnsafe.user.id;
    const url = `http://localhost:5000/send_result/${userId}`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ score: score })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log('Result sent successfully');
        } else {
            console.error('Failed to send result');
        }
    })
    .catch(error => console.error('Error:', error));
}
