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
