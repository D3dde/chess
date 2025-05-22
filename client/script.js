if (localStorage.getItem("theme") == "light-mode") {
  toggleDarkLight(document.getElementById("theme-toggle"));
}

function debug(x) {
  console.log("LOG | " + x);
}

function mode(mode) {
  switch (mode) {
    case 0:
      console.log("LOG | singleplayer");
      window.location.href = "./game.html";
      break;
    case 1:
      console.log("LOG | multiplayer");
      window.location.href = "./game.html";
      break;
    case 2:
      console.log("LOG | leaderboard");
      window.location.href = "leaderboard.html";
      break;
  }
}

function toggleDarkLight(self) {
  if (document.body.classList.contains("light-mode")) {
    console.log("LOG | switch to dark mode");
    document.body.setAttribute("class", "dark-mode");
    self.innerHTML = "&#xf4ee";
    localStorage.setItem("theme", "dark-mode");
  } else {
    console.log("LOG | switch to light mode");
    document.body.setAttribute("class", "light-mode");
    self.innerHTML = "&#xf522";
    localStorage.setItem("theme", "light-mode");
  }
}

// Game logic

let selectedSquare = null;

// Function to handle square clicks
function handleSquareClick(square) {
  console.log("LOG | Square: " + square.id);

  // If null
  if (!selectedSquare) {
    // First square
    selectedSquare = square;
    square.classList.add("selected");
  } else {
    // Second square
    let moveString = selectedSquare.id + square.id;
    console.log("LOG | Move: " + moveString);

    // Reset selection

    selectedSquare.classList.remove("selected");
    selectedSquare = null;

    const message = JSON.stringify({ command: "move", value: moveString });
    sendMessage(message);
  }
}

function updateChessboardFromFEN(fen) {
  console.log("LOG | updating chessboard");

  const chessboard = document.getElementById("chessboard");

  const squares = chessboard.querySelectorAll(".square");
  squares.forEach((square) => {
    square.innerHTML = "";
  });

  const positionPart = fen.split(" ")[0];

  const pieceMap = {
    r: '<span class="black-piece">♜</span>',
    n: '<span class="black-piece">♞</span>',
    b: '<span class="black-piece">♝</span>',
    q: '<span class="black-piece">♛</span>',
    k: '<span class="black-piece">♚</span>',
    p: '<span class="black-piece">♟</span>',
    R: '<span class="white-piece">♜</span>',
    N: '<span class="white-piece">♞</span>',
    B: '<span class="white-piece">♝</span>',
    Q: '<span class="white-piece">♛</span>',
    K: '<span class="white-piece">♚</span>',
    P: '<span class="white-piece">♟</span>',
  };

  const rows = positionPart.split("/");

  for (let i = 0; i < 8; i++) {
    let col = 0;

    for (let j = 0; j < rows[i].length; j++) {
      const char = rows[i].charAt(j);

      if (isNaN(char)) {
        const file = String.fromCharCode(97 + col); // 'a' + offset
        const rank = 8 - i; // Le righe FEN vanno dall'alto verso il basso
        const squareId = `${file}${rank}`;
        const square = chessboard.querySelector(`#${squareId}`);

        if (square) {
          square.innerHTML = pieceMap[char] || "";
        }

        col++;
      } else {
        col += parseInt(char, 10);
      }
    }
  }
}

let socket;

function startGame() {
  socket = new WebSocket("ws://localhost:8888");
  startClock()

  socket.onopen = function (event) {
    console.log("LOG | socket connected");
  };

  socket.onmessage = function (event) {
    try{
      const data = JSON.parse(event.data);
      console.log("LOG | data received: " + data.command);
      if (data.command == "fen") {
        updateChessboardFromFEN(data.value);
      }else if(data.command == "gameover"){
        Document.getElementById("game-status").innerHTML= data.value
      }
    } catch (err) {
      console.error(err)
    }
  };

  socket.onerror = function (event) {
    console.error("LOG | WebSocket error:", event);
  };

}

function quit(){
  console.log("LOG | quit");
  socket.close();
  window.location.href = "./index.html";
}

function sendMessage(message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(message);
  } else {
    console.warn("LOG | Cannot send message: WebSocket not connected");
  }
}


function startClock(){
  const timer = document.getElementById("timer");
  let seconds = 0;
  let minutes = 0;
  setInterval(() => {
          seconds++;
          if (seconds === 60) {
            seconds = 0;
            minutes++;
          }
          if (minutes === 60) {
            minutes = 0;
          }
          timer.innerHTML=minutes+':'+seconds;
        }, 1000);
}