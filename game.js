const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const W = 600, H = 400, CELL = 20;
const COLS = W / CELL, ROWS = H / CELL;

let state = "menu";
let snake, direction, food, foodType, score, speed, gameOver, powerup, powerupEnd;
let lastMove = 0, weedFirstClick = false, weedLastTime = 0;
const WEED_WINDOW = 250;
let highscore = Number(localStorage.getItem("standaHighscore") || 0);

function randPos() {
  return {
    x: Math.floor(Math.random() * COLS) * CELL,
    y: Math.floor(Math.random() * ROWS) * CELL
  };
}
function spawnFood() {
  const r = Math.random();
  let type = r < .10 ? "cocaine" :
             r < .20 ? "weed" :
             r < .25 ? "mushroom" :
             r < .40 ? "beer" : "normal";
  return {pos: randPos(), type};
}
function resetGame() {
  snake = [{x:100,y:100}];
  direction = {x:CELL,y:0};
  const f = spawnFood();
  food = f.pos; foodType = f.type;
  score = 0; speed = 6; gameOver = false;
  powerup = null; powerupEnd = 0;
  lastMove = performance.now();
}
function beep(freq=440, duration=.08, type="square") {
  try {
    const a = new AudioContext();
    const o = a.createOscillator(), g = a.createGain();
    o.type = type; o.frequency.value = freq;
    g.gain.setValueAtTime(.05, a.currentTime);
    g.gain.exponentialRampToValueAtTime(.001, a.currentTime + duration);
    o.connect(g); g.connect(a.destination); o.start(); o.stop(a.currentTime + duration);
  } catch(e) {}
}
function eatSound(type) {
  if (type === "beer") beep(180,.12,"sine");
  else if (type === "cocaine") beep(900,.12);
  else if (type === "weed") beep(250,.18,"sine");
  else if (type === "mushroom") beep(120,.25,"sawtooth");
  else beep(600,.06);
}
function gameOverSound() { beep(90,.35,"sawtooth"); }

function keydown(e) {
  if (["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Enter","r","R"].includes(e.key))
    e.preventDefault();

  if (state === "menu" && e.key === "Enter") {
    state = "game"; resetGame(); beep(500,.08);
    return;
  }
  if (state !== "game") return;

  if (gameOver && (e.key === "r" || e.key === "R")) {
    resetGame(); return;
  }

  if (powerup === "weed" && ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) {
    const now = performance.now();
    if (!weedFirstClick) {
      weedFirstClick = true; weedLastClick = now; return;
    }
    if (now - weedLastClick <= WEED_WINDOW) {
      weedFirstClick = false;
    } else {
      weedFirstClick = true; weedLastClick = now; return;
    }
  }

  if (e.key === "ArrowUp" && direction.y !== CELL) direction={x:0,y:-CELL};
  else if (e.key === "ArrowDown" && direction.y !== -CELL) direction={x:0,y:CELL};
  else if (e.key === "ArrowLeft" && direction.x !== CELL) direction={x:-CELL,y:0};
  else if (e.key === "ArrowRight" && direction.x !== -CELL) direction={x:CELL,y:0};
}
window.addEventListener("keydown", keydown);

function drawText(text,x,y,size,color="#fff") {
  ctx.fillStyle=color; ctx.font=`${size}px Arial`; ctx.fillText(text,x,y);
}
function draw() {
  const now = performance.now();
  const tripMode = powerup === "mushroom" && now < powerupEnd;
  if (tripMode) ctx.fillStyle=`rgb(${Math.random()*50},${Math.random()*50},${Math.random()*50})`;
  else ctx.fillStyle="#000";
  ctx.fillRect(0,0,W,H);

  if (state === "menu") {
    drawText("Standa a jeho pivka",120,145,40);
    drawText("ENTER",200,205,28,"#aaa");
    drawText("Highscore: "+highscore,200,265,28,"#ffd700");
    requestAnimationFrame(draw); return;
  }

  const offset = tripMode ? Math.floor(Math.random()*21)-10 : 0;
  for(let x=0;x<=W;x+=CELL) {
    ctx.strokeStyle=tripMode ? `rgb(${Math.random()*255},${Math.random()*255},${Math.random()*255})` : "#1e1e1e";
    ctx.beginPath(); ctx.moveTo(x+offset,0); ctx.lineTo(x+offset,H); ctx.stroke();
  }
  for(let y=0;y<=H;y+=CELL) {
    ctx.strokeStyle=tripMode ? `rgb(${Math.random()*255},${Math.random()*255},${Math.random()*255})` : "#1e1e1e";
    ctx.beginPath(); ctx.moveTo(0,y+offset); ctx.lineTo(W,y+offset); ctx.stroke();
  }

  // Food
  if(foodType==="cocaine") ctx.fillStyle="#fff";
  else if(foodType==="weed") ctx.fillStyle="#00ff00";
  else if(foodType==="mushroom") ctx.fillStyle="#f00";
  else if(foodType==="beer") ctx.fillStyle="#ffc800";
  else ctx.fillStyle="#f00";
  ctx.fillRect(food.x,food.y,CELL,CELL);
  if(foodType==="mushroom" || foodType==="beer") {
    ctx.fillStyle="#fff"; ctx.fillRect(food.x,food.y,CELL,6);
  }

  for(let i=0;i<snake.length;i++) {
    ctx.fillStyle=tripMode ? `rgb(${Math.random()*255},${Math.random()*255},${Math.random()*255})`
      : (i===0 ? "#d2b494" : (i%2===0 ? "#0078ff" : "#fff"));
    ctx.fillRect(snake[i].x,snake[i].y,CELL,CELL);
  }

  drawText("Score: "+score,10,25,20);
  if(powerup && now < powerupEnd) drawText(`${powerup}: ${Math.max(0,Math.floor((powerupEnd-now)/1000))}s`,10,50,20);

  if(gameOver) {
    drawText("GAME OVER",200,175,40);
    drawText("R restart",220,215,24,"#aaa");
    drawText("Highscore: "+highscore,200,255,24,"#ffd700");
  }
  requestAnimationFrame(draw);
}

function update(now) {
  if(state==="game" && !gameOver) {
    let finalSpeed=speed;
    if(powerup==="cocaine") finalSpeed*=1.25;
    if(powerup==="weed") finalSpeed*=.5;
    const interval=1000/Math.max(5,finalSpeed);
    if(now-lastMove>=interval) {
      lastMove=now;
      const head={x:snake[0].x+direction.x,y:snake[0].y+direction.y};
      if(head.x<0||head.x>=W||head.y<0||head.y>=H||snake.some(s=>s.x===head.x&&s.y===head.y)) {
        gameOver=true; gameOverSound();
        if(score>highscore) { highscore=score; localStorage.setItem("standaHighscore",highscore); }
      } else {
        snake.unshift(head);
        if(head.x===food.x&&head.y===food.y) {
          if(["cocaine","weed","mushroom"].includes(foodType)) {
            powerup=foodType;
            score+=5;
            powerupEnd=now+(foodType==="mushroom"?20000:15000);
            eatSound(foodType);
          } else if(foodType==="beer") { score+=3; eatSound("beer"); }
          else { score+=1; eatSound("normal"); }
          const f=spawnFood(); food=f.pos; foodType=f.type;
        } else snake.pop();
      }
    }
    if(powerup && now>=powerupEnd) powerup=null;
  }
  requestAnimationFrame(update);
}
resetGame();
draw();
requestAnimationFrame(update);
