// 1. Collect all audio elements on the page
const audios = Array.from(document.querySelectorAll("audio"));

// 2. Find the playlist button (may not exist on all pages)
const playAllBtn = document.getElementById("play-all");

// Safety check: if no button or no audio, do nothing
if (!playAllBtn || audios.length === 0) {
  console.log("Playlist not activated on this page.");
} else {

  let currentIndex = 0;
  let playlistActive = false;

  function playFrom(index) {
    if (index >= audios.length) {
		playlistActive = false;
		currentIndex = 0;
		playAllBtn.textContent = "▶️ Play all clips on this page";
		audios.forEach(a => a.currentTime = 0);
		return;
    }

    currentIndex = index;

    audios[index].scrollIntoView({
      behavior: "smooth",
      block: "nearest"
    });

    audios[index].play();
  }

  // 3. When a clip ends, advance playlist
  audios.forEach((audio, index) => {

    audio.addEventListener("ended", () => {
      if (playlistActive && index === currentIndex) {
        playFrom(index + 1);
      }
    });

    // 4. When user plays manually, stop playlist mode
    audio.addEventListener("play", () => {
      audios.forEach(other => {
        if (other !== audio) other.pause();
      });

      if (!playlistActive) {
        currentIndex = index;
		playAllBtn.textContent = "▶️ Play all clips on this page";
      }
    });
  });

  // 5. Playlist button behavior
playAllBtn.addEventListener("click", () => {

  // If playlist not active → start
  if (!playlistActive) {
    playlistActive = true;
    playAllBtn.textContent = "⏸ Pause playlist";
    playFrom(currentIndex);
  }

  // If active and playing → pause
  else if (!audios[currentIndex].paused) {
    audios[currentIndex].pause();
    playAllBtn.textContent = "▶️ Resume playlist";
  }

  // If active but paused → resume
  else {
    audios[currentIndex].play();
    playAllBtn.textContent = "⏸ Pause playlist";
  }
});
document.querySelectorAll("[data-play-group]").forEach(btn => {

  btn.addEventListener("click", () => {

    const group = btn.dataset.playGroup;

    const groupAudios = Array.from(
      document.querySelectorAll(`[data-group="${group}"] audio`)
    );

    if (!groupAudios.length) return;

    stopAll();

    activePlaylist = groupAudios;
    currentIndex = 0;
    playlistActive = true;

    playFrom(0);
  });

});
}