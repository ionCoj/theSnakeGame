
let snakeX = 50;
let snakeY = 50;
let foodRadius = 10;
let score = 0;
let snakeSpeed = 25;
let snakeLength = 20;
let snakeWidth = 20;
let downPressed = false;
let upPressed = false;
let leftPressed = false;
let rightPressed = false;
let snakeParts = [];
let blockSize = 25;
let total = 30;
let foodX = (Math.floor(Math.random() * total))*blockSize;
let foodY = (Math.floor(Math.random() * total))*blockSize;



window.onload = function() {
  canvas = document.getElementById('gameArena');
  canvas.width = blockSize * total;
  canvas.height = blockSize * total;
  ctx = canvas.getContext('2d');
  setInterval(drawGame, 1000/10);
}

function drawGame(){
  clearScreen();
  drawFood();
  updateScore();
  drawSnake();
  boundryCheck();
}

function updateScore(){
  if(snakeX == foodX && snakeY == foodY){
    score += 1;
    snakeParts.push([foodX, foodY]);
    foodX = Math.floor(Math.random() * total)*blockSize;
    foodY = Math.floor(Math.random() * total)*blockSize;
  }
}

function boundryCheck(){
  if(snakeY < 0 || snakeY > canvas.height - snakeWidth || snakeX < 0 ||snakeX > canvas.width - snakeWidth){
    resetGame();
  }
  for (let i = 0; i < snakeParts.length; i++) {
    if (snakeParts[i][0] == snakeX && snakeParts[i][1] == snakeY) {
        resetGame();
    }
  }
  }

function resetGame(){
  alert("Game Over!" + "\nYour Score: " + score);
  snakeX = 50;
  snakeY = 50;
  length = 20;
  downPressed = false;
  upPressed = false;
  leftPressed = false;
  rightPressed = false;
  score = 0;
  snakeParts = [];
}

function clearScreen(){
ctx.fillStyle = 'black';
ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawSnake(){
  
  for (let i = snakeParts.length - 1; i > 0; i--) {
    snakeParts[i] = snakeParts[i - 1];
  }
  if (snakeParts.length) {
        snakeParts[0] = [snakeX, snakeY];
    }
  ctx.fillStyle = 'green';
  // Inputs:
  if(downPressed){
    snakeY += snakeSpeed;
  }
  if(upPressed){
    snakeY -= snakeSpeed;
  }
  if(leftPressed){
    snakeX -= snakeSpeed;
  }
  if(rightPressed){
    snakeX += snakeSpeed;
  }
  ctx.fillRect(snakeX, snakeY, snakeLength, snakeWidth);
  for (let i = 0; i < snakeParts.length; i++) {
        ctx.fillStyle = 'green';
        ctx.fillRect(snakeParts[i][0], snakeParts[i][1], snakeLength, snakeWidth);
}
}

function drawFood(){
  ctx.beginPath();
  ctx.fillStyle = 'red';
  ctx.fillRect(foodX, foodY,snakeLength, snakeWidth);
  ctx.fill();
}

document.addEventListener('keydown', keyDown);

function keyDown(event){
  if(event.keyCode == 40 && !upPressed){
    downPressed = true;
    upPressed = false;
    leftPressed = false;
    rightPressed = false;
  }
  if(event.keyCode == 38 && !downPressed){
    downPressed = false;
    upPressed = true;
    leftPressed = false;
    rightPressed = false;
  }
  if(event.keyCode == 39 && !leftPressed){
    downPressed = false;
    upPressed = false;
    leftPressed = false;
    rightPressed = true;
  }
  if(event.keyCode == 37 && !rightPressed){
    downPressed = false;
    upPressed = false;
    leftPressed = true;
    rightPressed = false;
  }
}
