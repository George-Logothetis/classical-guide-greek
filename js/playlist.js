// ============================
// PLAYLIST ENGINE (Static-Safe)
// ============================

(function () {

  const playlists = {};
  let currentPlaylistName = null;
  let playlistInitiatedPlay = false;

  const HOLD_THRESHOLD = 600; // ms for long press

  // ---------------------------------
  // Utility: stop all audio globally
  // ---------------------------------
  function stopAllAudio() {
    document.querySelectorAll("audio").forEach(a => a.pause());
  }

// ---------------------------------
// Visual State Update
// ---------------------------------
function updateVisualState(name) {
  const playlist = playlists[name];
  if (!playlist || !playlist.container) return;

  const currentAudio = playlist.audios[playlist.index];
  const hasProgress =
    currentAudio && currentAudio.currentTime > 0;

// Remove paused-playlist marker from all clips
	playlist.audios.forEach(audio => {
		const rec = audio.closest(".recording");
		if (rec) rec.classList.remove("paused-playlist");
	});

  // Remove all state classes
  playlist.container.classList.remove(
    "playlist-idle",
    "playlist-playing",
    "playlist-paused"
  );

if (playlist.active) {
  playlist.container.classList.add("playlist-playing");

} else if (currentPlaylistName === name) {
  playlist.container.classList.add("playlist-paused");

  const rec = playlist.audios[playlist.index].closest(".recording");
  if (rec) rec.classList.add("paused-playlist");

} else {
  playlist.container.classList.add("playlist-idle");
}

  // ---- Toggle button label update ----
  if (playlist.toggleBtn) {
    if (playlist.active) {
      playlist.toggleBtn.textContent = "⏸ Pause";
    } else if (hasProgress) {
      playlist.toggleBtn.textContent = "▶ Resume";
    } else {
      playlist.toggleBtn.textContent = "▶ Start";
    }
  }
}
  // ---------------------------------
  // Highlight currently playing recording
  // ---------------------------------
  function highlightRecording(audio) {
    document.querySelectorAll(".recording.playing")
      .forEach(el => el.classList.remove("playing"));

    const rec = audio.closest(".recording");
    if (rec) rec.classList.add("playing");
  }

  function clearRecordingHighlight() {
    document.querySelectorAll(".recording.playing")
      .forEach(el => el.classList.remove("playing"));
  }

  // ---------------------------------
  // Register a playlist
  // ---------------------------------
  window.registerPlaylist = function (name, audioElements, containerElement) {

    if (!audioElements || !audioElements.length) return;

    playlists[name] = {
      audios: audioElements,
      index: 0,
      active: false,
      container: containerElement
    };

    updateVisualState(name);
  };

  // ---------------------------------
  // Attach controls to a playlist
  // ---------------------------------
  window.attachPlaylistControls = function (name, toggleBtn, nextBtn) {

    const playlist = playlists[name];
    if (!playlist) return;
	
	playlist.toggleBtn = toggleBtn;

    // ---- Toggle Button ----
    toggleBtn.addEventListener("click", () => {

      // Pause another playlist if active
      if (currentPlaylistName && currentPlaylistName !== name) {
        pausePlaylist(currentPlaylistName);
      }

      // If not active → start/resume
      if (!playlist.active) {

        playlist.active = true;
        currentPlaylistName = name;

        playCurrent(name);

      } else {
        pausePlaylist(name);
      }

      updateVisualState(name);
    });

    // ---- Next Button (short vs long) ----
    let holdTimer = null;

    nextBtn.addEventListener("pointerdown", () => {

      holdTimer = setTimeout(() => {
        resetPosition(name);
        holdTimer = null;
      }, HOLD_THRESHOLD);

    });

    nextBtn.addEventListener("pointerup", () => {

      if (holdTimer) {
        clearTimeout(holdTimer);
        skipNext(name);
      }

    });

    nextBtn.addEventListener("pointerleave", () => {
      if (holdTimer) {
        clearTimeout(holdTimer);
        holdTimer = null;
      }
    });
  };

  // ---------------------------------
  // Play current clip
  // ---------------------------------
  function playCurrent(name) {

    const playlist = playlists[name];
    if (!playlist) return;

    const audio = playlist.audios[playlist.index];
    if (!audio) return;
// Pause all OTHER audios, but do not call global stop
	document.querySelectorAll("audio").forEach(a => {
		if (a !== audio) a.pause();
	});

	clearRecordingHighlight();

///	audio.currentTime = 0;
	playlistInitiatedPlay = true;

	audio.play()
		.catch(() => {})
		.finally(() => {
			playlistInitiatedPlay = false;
		});
/// Back to normal
    highlightRecording(audio);

    audio.onended = () => {

      playlist.index++;

      if (playlist.index >= playlist.audios.length) {
        // Natural end
        playlist.active = false;
        playlist.index = 0;
		playlist.audios[0].currentTime = 0;
        currentPlaylistName = null;

        clearRecordingHighlight();
        updateVisualState(name);
        return;
      }

      playCurrent(name);
    };

    updateVisualState(name);
  }

// ---------------------------------
// Pause playlist
// ---------------------------------
function pausePlaylist(name) {

  const playlist = playlists[name];
  if (!playlist) return;

  const audio = playlist.audios[playlist.index];
  if (audio) audio.pause();

  playlist.active = false;

  // DO NOT clear currentPlaylistName here.
  // Pausing is suspension, not termination.

  clearRecordingHighlight();
  updateVisualState(name);
}

  // ---------------------------------
  // Skip to next (short press)
  // ---------------------------------
  function skipNext(name) {

    const playlist = playlists[name];
    if (!playlist) return;

    const wasPlaying = playlist.active;

    const currentAudio = playlist.audios[playlist.index];
    if (currentAudio) currentAudio.pause();

    playlist.index++;

    if (playlist.index >= playlist.audios.length) {
      // behave like natural end
      playlist.index = 0;
      playlist.active = false;
      currentPlaylistName = null;

      clearRecordingHighlight();
      updateVisualState(name);
      return;
    } else {
		playlist.audios[playlist.index].currentTime = 0;
	}

    if (wasPlaying) {
      currentPlaylistName = name;
      playlist.active = true;
      playCurrent(name);
    } else {
      updateVisualState(name);
    }
  }

  // ---------------------------------
  // Long press reset (position only)
  // ---------------------------------
  function resetPosition(name) {

    const playlist = playlists[name];
    if (!playlist) return;

    const wasPlaying = playlist.active;

    const audio = playlist.audios[playlist.index];
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }

    playlist.index = 0;

    if (wasPlaying) {
      currentPlaylistName = name;
      playCurrent(name);
    } else {
      clearRecordingHighlight();
      updateVisualState(name);
    }
  }

  // ---------------------------------
  // Manual audio play handling
  // ---------------------------------
document.addEventListener("DOMContentLoaded", () => {
document.querySelectorAll("audio").forEach(audio => {

  audio.addEventListener("play", () => {

    // Ignore plays initiated by playlist engine
    if (playlistInitiatedPlay) return;

    // Pause active playlist
    if (currentPlaylistName) {
      pausePlaylist(currentPlaylistName);
    }

    // Pause all other audios
    document.querySelectorAll("audio").forEach(other => {
      if (other !== audio) other.pause();
    });

    clearRecordingHighlight();
    highlightRecording(audio);
  });

});
});

})();

// ---------------------------------
// Auto-register global playlist
// ---------------------------------

document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll(".playlist-container").forEach(container => {

    const name = container.dataset.playlist;
    if (!name) return;

    // IMPORTANT: only use controls belonging to THIS container
    const toggleBtn = container.querySelector(":scope > .playlist-controls .toggle");
    const nextBtn   = container.querySelector(":scope > .playlist-controls .next");

    if (!toggleBtn || !nextBtn) return;

    registerPlaylist(
      name,
      Array.from(container.querySelectorAll("audio")),
      container
    );

    attachPlaylistControls(name, toggleBtn, nextBtn);

  });

});