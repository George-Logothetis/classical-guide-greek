  const audios = Array.from(document.querySelectorAll("audio"));
  const playAllBtn = document.getElementById("play-all");

  let currentIndex = 0;
  let playlistActive = false;

  function playFrom(index) {
    if (index >= audios.length) {
      playlistActive = false;
      currentIndex = 0;
      return;
    }

    currentIndex = index;
    audios[index].play();
  }

  audios.forEach((audio, index) => {
    audio.addEventListener("ended", () => {
      if (playlistActive && index === currentIndex) {
        playFrom(index + 1);
      }
    });

    audio.addEventListener("play", () => {
      // stop other players
      audios.forEach(other => {
        if (other !== audio) other.pause();
      });

      // if user clicked manually, exit playlist mode
      if (!playlistActive) currentIndex = index;
    });
  });

  playAllBtn.addEventListener("click", () => {
    playlistActive = true;
    playFrom(0);
  });