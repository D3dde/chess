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
      window.location.href = "./singleplayer.html";
      break;
    case 1:
      console.log("LOG | multiplayer");
      const roomId = document.getElementById("room").value.trim();
      if (roomId === "") {
        alert("Please enter a room ID");
        return;
      }
      localStorage.setItem("roomId", roomId);
      window.location.href = "./multiplayer.html";
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
let socket;
let gameMode = null;
let playerColor = null;
let currentTurn = 'white';
let isSpectator = false;

// Function to handle square clicks
function handleSquareClick(square) {
  console.log("LOG | Square: " + square.id);

  // In multiplayer, check if it's the player's turn
  if (gameMode === 'multiplayer' && !isSpectator) {
    if (currentTurn !== playerColor) {
      updateGameStatus("It's not your turn!");
      return;
    }
  }

  // If null
  if (!selectedSquare) {
    // First square - only allow selection if there's a piece and it's the right color
    if (gameMode === 'multiplayer' && !isSpectator) {
      const piece = square.querySelector('span');
      if (!piece) return; // No piece to select
      
      const isWhitePiece = piece.classList.contains('white-piece');
      const isBlackPiece = piece.classList.contains('black-piece');
      
      if ((playerColor === 'white' && !isWhitePiece) || 
          (playerColor === 'black' && !isBlackPiece)) {
        updateGameStatus("You can only move your own pieces!");
        return;
      }
    }
    
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
        const rank = 8 - i; // FEN rows go from top to bottom
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

function updateGameStatus(message) {
  const statusElement = document.getElementById("game-status");
  if (statusElement) {
    statusElement.innerHTML = message;
  }
}

function singleplayer() {
  gameMode = 'singleplayer';
  socket = new WebSocket("ws://localhost:8888");
  startClock();

  socket.onopen = function (event) {
    console.log("LOG | socket connected");
    // Send mode identification
    const message = JSON.stringify({ mode: "singleplayer" });
    socket.send(message);
  };

  socket.onmessage = function (event) {
    try {
      const data = JSON.parse(event.data);
      console.log("LOG | data received: " + data.command);
      
      if (data.command == "fen") {
        updateChessboardFromFEN(data.value);
      } else if (data.command == "gameover") {
        updateGameStatus("Game Over: " + data.value);
      }
    } catch (err) {
      console.error(err);
    }
  };

  socket.onerror = function (event) {
    console.error("LOG | WebSocket error:", event);
  };
}

function multiplayer() {
  gameMode = 'multiplayer';
  const roomId = localStorage.getItem("roomId") || "default";
  
  socket = new WebSocket("ws://localhost:8888");

  socket.onopen = function (event) {
    console.log("LOG | socket connected to multiplayer");
    // Send mode identification with room ID
    const message = JSON.stringify({ mode: "multiplayer", room_id: roomId });
    socket.send(message);
  };

  socket.onmessage = function (event) {
    try {
      const data = JSON.parse(event.data);
      console.log("LOG | data received: " + data.command);
      
      if (data.command == "fen") {
        updateChessboardFromFEN(data.value);
      } else if (data.command == "gameover") {
        updateGameStatus("Game Over: " + data.value);
      } else if (data.command == "color") {
        playerColor = data.value;
        updateGameStatus(`You are playing as ${playerColor}`);
        console.log("LOG | Player color: " + playerColor);
      } else if (data.command == "turn") {
        currentTurn = data.value;
        if (isSpectator) {
          updateGameStatus(`Current turn: ${currentTurn}`);
        } else if (currentTurn === playerColor) {
          updateGameStatus("Your turn!");
        } else {
          updateGameStatus(`Waiting for ${currentTurn} player...`);
        }
      } else if (data.command == "spectator") {
        isSpectator = true;
        updateGameStatus("Spectating - Game is full");
        console.log("LOG | Player is spectating");
      } else if (data.command == "game_ready") {
        startClock();
        updateGameStatus(data.value);
        console.log("LOG | Both players connected");
      } else if (data.command == "waiting") {
        updateGameStatus(data.value);
        console.log("LOG | Waiting for second player");
      } else if (data.command == "spectator") {
        isSpectator = true;
        updateGameStatus("Spectating - Game is full");
        console.log("LOG | Player is spectating");
      } else if (data.command == "player_left") {
        updateGameStatus("Player disconnected: " + data.value);
        console.log("LOG | " + data.value);
      } else if (data.command == "invalid_move") {
        updateGameStatus(data.value);
      } else if (data.command == "error") {
        updateGameStatus("Error: " + data.value);
      }
    } catch (err) {
      console.error(err);
    }
  };

  socket.onerror = function (event) {
    console.error("LOG | WebSocket error:", event);
  };

  socket.onclose = function (event) {
    updateGameStatus("Disconnected from server");
  };
}

function quit() {
  console.log("LOG | quit");
  if (socket) {
    socket.close();
  }
  window.location.href = "./index.html";
}

function sendMessage(message) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(message);
  } else {
    console.warn("LOG | Cannot send message: WebSocket not connected");
  }
}

function startClock() {
  const timer = document.getElementById("timer");
  if (!timer) return;
  
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
    timer.innerHTML = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
  }, 1000);
}