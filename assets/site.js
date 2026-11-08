document.addEventListener('DOMContentLoaded', () => {
  // Mobile menu toggle
  const toggleBtn = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  if (toggleBtn && nav) {
    toggleBtn.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
  }

  // Audio players on Hörbeispiele
  initAudioPlayers();
});

function formatTime(sec) {
  if (!isFinite(sec) || sec < 0) return '00:00';
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function initAudioPlayers() {
  const tracks = document.querySelectorAll('.audio-track');
  let activeAudio = null;
  let activeContainer = null;

  const playIcon = `<svg viewBox="0 0 18 20"><path d="M17.29,9.02 C18.25,9.56 18.25,10.44 17.29,10.98 L1.74,19.78 C0.78,20.33 0,19.87 0,18.76 L0,1.24 C0,0.13 0.78,-0.32 1.74,0.22 L17.29,9.02 Z"></path></svg>`;
  const pauseIcon = `<svg viewBox="0 0 18 20"><rect x="2" y="1" width="5" height="18" rx="1"></rect><rect x="11" y="1" width="5" height="18" rx="1"></rect></svg>`;

  tracks.forEach((trackEl) => {
    const audio = trackEl.querySelector('audio');
    const btn = trackEl.querySelector('.play-btn');
    const range = trackEl.querySelector('.track-progress');
    const timeEl = trackEl.querySelector('.track-time');
    const defaultDur = trackEl.dataset.duration || '00:30';

    if (!audio || !btn) return;

    btn.addEventListener('click', () => {
      if (activeAudio && activeAudio !== audio) {
        activeAudio.pause();
        if (activeContainer) {
          activeContainer.classList.remove('playing');
          const prevBtn = activeContainer.querySelector('.play-btn');
          if (prevBtn) prevBtn.innerHTML = playIcon;
        }
      }

      if (audio.paused) {
        audio.play();
        activeAudio = audio;
        activeContainer = trackEl;
        trackEl.classList.add('playing');
        btn.innerHTML = pauseIcon;
      } else {
        audio.pause();
        trackEl.classList.remove('playing');
        btn.innerHTML = playIcon;
      }
    });

    audio.addEventListener('timeupdate', () => {
      const dur = audio.duration || 30;
      if (range) {
        range.max = dur;
        range.value = audio.currentTime;
      }
      if (timeEl) {
        timeEl.textContent = `${formatTime(audio.currentTime)} / ${ isFinite(audio.duration) ? formatTime(audio.duration) : defaultDur }`;
      }
    });

    audio.addEventListener('loadedmetadata', () => {
      if (range && isFinite(audio.duration)) {
        range.max = audio.duration;
      }
      if (timeEl && isFinite(audio.duration)) {
        timeEl.textContent = `00:00 / ${formatTime(audio.duration)}`;
      }
    });

    audio.addEventListener('ended', () => {
      trackEl.classList.remove('playing');
      btn.innerHTML = playIcon;
      if (range) range.value = 0;
    });

    if (range) {
      range.addEventListener('input', () => {
        audio.currentTime = Number(range.value);
      });
    }
  });
}
