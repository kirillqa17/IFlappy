Telegram.WebApp.ready();
Telegram.WebApp.expand(); // Make the web app fullscreen

const canvas = document.getElementById('gameCanvas');
const context = canvas.getContext('2d');

const birdImg = new Image();
birdImg.src = 'images/sasha.jpg';

const pipeNorthImg = new Image();
pipeNorthImg.src = 'images/chlen_vniz.jpg';

const pipeSouthImg = new Image();
pipeSouthImg.src = 'images/chlen_vverh.jpg';

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
const pipeWidth = 150;
const gap = 200;

let frame = 0;
let score = 0;

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);

    context.drawImage(birdImg, bird.x, bird.y, bird.width, bird.height);

    bird.velocity += bird.gravity;
    bird.y += bird.velocity;

    if (bird.y + bird.height > canvas.height || bird.y < 0) {
        resetGame();
    }

    if (frame % 150 === 0) {
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
        }

        context.drawImage(pipeNorthImg, pipes[i].x, pipes[i].y, pipeWidth, canvas.height);
        context.drawImage(pipeSouthImg, pipes[i].x, pipes[i].y + canvas.height + gap, pipeWidth, canvas.height);

        if (
            bird.x + bird.width > pipes[i].x &&
            bird.x < pipes[i].x + pipeWidth &&
            (bird.y < pipes[i].y + canvas.height || bird.y + bird.height > pipes[i].y + canvas.height + gap)
        ) {
            resetGame();
        }
    }

    context.fillStyle = "#000";
    context.font = "20px Arial";
    context.fillText("Score: " + score, 10, 20);

    frame++;
    setTimeout(draw, 1000 / 60);
}

function resetGame() {
    bird.y = 150;
    bird.velocity = 0;
    pipes.length = 0;
    score = 0;
    frame = 0;
}

canvas.addEventListener('click', () => {
    bird.velocity = bird.lift;
});

document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        bird.velocity = bird.lift;
    }
});

draw();
