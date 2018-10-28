/**
 * @author ALbert Koczy 2018
 */
(function() {
  let started = false;
  const canvas = document.querySelector("#pongCanvas");
  // canvas size
  const c = canvas.getContext("2d");
  const w = canvas.width,
    h = canvas.height;
  let y1 = h / 2;
  let y2 = h / 2;
  // paddle size
  const pWidth = 10;
  const pHeight = 50;
  // paddle speed
  const speed = 14;
  // ball size
  const bsize = 10;

  // cpu difficulty
  let cpuSpeed = 10;

  let bx = w / 2,
    by = h / 2;

  // ball velocity
  let vx = 0,
    vy = 0;

  let playerScore = 0;
  let cpuScore = 0;
  function resetBall() {
    vx = 0; // stop the ball
    vy = 0;
    bx = w / 2; // move it to the center
    by = h / 2;
    setTimeout(function() {
      // wait a bit before the launch not to suprise the player
      vx = random(0, 5);
      vy = random(0, 5);
      if (Math.random() > 0.5) {
        // randomize direction
        vx *= -1;
      }
      if (Math.random() > 0.5) {
        vy *= -1;
      }
    }, 1000);
  }
  function random(max, min) {
    return Math.random() * (max - min) + min;
  }
  function loop() {
    c.fillStyle = "black";
    c.fillRect(0, 0, w, h); // clear screen
    c.fillStyle = "white";

    c.fillRect(0, y1, pWidth, pHeight); // draw left paddle
    c.fillRect(w - pWidth, y2, pWidth, pHeight); // draw right paddle
    c.fillRect(bx, by, bsize, bsize); // draw ball
    c.font = "40px Arial";
    c.textAlign = "center";
    c.fillText(playerScore + "               " + cpuScore, w / 2, h * 0.2); // draw score
    bx += vx; // animate ball
    by += vy;
    if (by <= 0 || by + bsize >= h) {
      // bounce off top/bottom edge
      vy *= -1 * random(0.9, 1.1);
    }
    // left paddle score check
    if (bx <= pWidth) {
      if (by >= y1 && by <= y1 + pHeight) {
        // bounced off the paddle
        vx *= -1.05;
        vy += random(-3, -3);
      } else {
        cpuScore++;
        resetBall();
      }
    }
    // right paddle score check
    if (bx + bsize >= w - pWidth) {
      if (by >= y2 && by <= y2 + pHeight) {
        // bounced off the paddle
        vx *= -1.05;
        vy += random(-3, -3);
      } else {
        playerScore++;
        if (cpuSpeed < 19) {
          cpuSpeed += 0.7;
        }
        resetBall();
      }
    }
    // cpu AI
    let paddleDist = by - (y2 + pHeight / 2);
    if (paddleDist != 0) {
      y2 += Math.min(
        Math.max(paddleDist / Math.abs(paddleDist), -cpuSpeed),
        cpuSpeed
      );
    }

    requestAnimationFrame(loop);
  }
  function startPong() {
    started = true;
    canvas.style.display = "block";
    resetBall();
    loop();
  }
  document.addEventListener("keydown", function(ev) {
    if (!started) return;
    // WA and arrows
    if ((ev.keyCode === 87 || ev.keyCode === 38) && y1 > 0) {
      y1 -= speed;
    }
    if ((ev.keyCode === 83 || ev.keyCode === 40) && y1 < h - pHeight) {
      y1 += speed;
    }
  });

  document.querySelector("#playPong").addEventListener("click", startPong);
})();
