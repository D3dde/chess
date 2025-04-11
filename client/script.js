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

function updateChessboardFromFEN( fen) {
  if (!fen) {
    console.error('LOG | there is no fen');
    return;
  }
  chessboardNode = document.getElementById("chessboard")
  // Pulisci tutte le caselle dalla scacchiera
  const squares = chessboardNode.querySelectorAll('.square');
  squares.forEach(square => {
    square.innerHTML = '';
  });
  
  // Ottieni solo la parte della posizione della notazione FEN (prima di eventuali spazi)
  const positionPart = fen.split(' ')[0];
  
  // Mappa dei pezzi FEN ai simboli Unicode
  const pieceMap = {
    'r': '<span class="black-piece">♜</span>',
    'n': '<span class="black-piece">♞</span>',
    'b': '<span class="black-piece">♝</span>',
    'q': '<span class="black-piece">♛</span>',
    'k': '<span class="black-piece">♚</span>',
    'p': '<span class="black-piece">♟</span>',
    'R': '<span class="white-piece">♜</span>',
    'N': '<span class="white-piece">♞</span>',
    'B': '<span class="white-piece">♝</span>',
    'Q': '<span class="white-piece">♛</span>',
    'K': '<span class="white-piece">♚</span>',
    'P': '<span class="white-piece">♟</span>'
  };
  
  // Converte la notazione FEN in una matrice di pezzi
  const rows = positionPart.split('/');
  
  // Cicla attraverso le righe
  for (let i = 0; i < 8; i++) {
    let row = rows[i];
    let col = 0;
    
    // Cicla attraverso i caratteri di ogni riga
    for (let j = 0; j < row.length; j++) {
      const char = row.charAt(j);
      
      // Se è un numero, salta quel numero di caselle
      if (!isNaN(char)) {
        col += parseInt(char, 10);
      } else {
        // Altrimenti posiziona il pezzo
        const file = String.fromCharCode(97 + col); // 'a' + offset
        const rank = 8 - i; // Le righe FEN vanno dall'alto verso il basso
        const squareId = `${file}${rank}`;
        const square = chessboardNode.querySelector(`#${squareId}`);
        
        if (square) {
          square.innerHTML = pieceMap[char] || '';
        }
        
        col++;
      }
    }
  }
}