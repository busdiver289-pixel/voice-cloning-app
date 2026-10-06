const API_BASE = '/api';

const state = {
  profile: {
    name: 'My Voice',
    pitch: 1.0,
    rate: 1.0,
    duration: 0,
    tags: ['Warm', 'Conversational', 'Balanced'],
    sampleUrl: '',
  },
};

const profileNameInput = document.getElementById('profileName');
const audioUploadInput = document.getElementById('audioUpload');
const audioPreview = document.getElementById('audioPreview');
const sampleSummary = document.getElementById('sampleSummary');
const styleTags = document.getElementById('styleTags');
const pitchValue = document.getElementById('pitchValue');
const rateValue = document.getElementById('rateValue');
const durationValue = document.getElementById('durationValue');
const pitchSlider = document.getElementById('pitchSlider');
const rateSlider = document.getElementById('rateSlider');
const scriptInput = document.getElementById('scriptInput');
const statusText = document.getElementById('statusText');
const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById('stopButton');
const generateButton = document.getElementById('generateButton');
const stopSpeechButton = document.getElementById('stopSpeechButton');
const saveProfileButton = document.getElementById('saveProfileButton');

let mediaRecorder;
let audioChunks = [];
let stream;

function setStatus(message) {
  statusText.textContent = message;
}

function renderProfile() {
  profileNameInput.value = state.profile.name || 'My Voice';
  pitchSlider.value = state.profile.pitch || 1.0;
  rateSlider.value = state.profile.rate || 1.0;
  pitchValue.textContent = Number(state.profile.pitch || 1.0).toFixed(1);
  rateValue.textContent = Number(state.profile.rate || 1.0).toFixed(1);
  durationValue.textContent = `${Number(state.profile.duration || 0).toFixed(1)}s`;

  styleTags.innerHTML = '';
  const tags = state.profile.tags && state.profile.tags.length ? state.profile.tags : ['Warm', 'Conversational', 'Balanced'];
  tags.forEach((tag) => {
    const item = document.createElement('li');
    item.textContent = tag;
    styleTags.appendChild(item);
  });

  if (state.profile.sampleUrl) {
    audioPreview.src = state.profile.sampleUrl;
    audioPreview.classList.remove('hidden');
    sampleSummary.textContent = `${Number(state.profile.duration || 0).toFixed(1)}s sample`;
  } else {
    audioPreview.classList.add('hidden');
    sampleSummary.textContent = 'No sample yet';
  }
}

function analyzeVoiceProfile(durationSeconds) {
  const presets = [
    ['Warm', 'Conversational', 'Balanced'],
    ['Focused', 'Clear', 'Confident'],
    ['Bright', 'Energetic', 'Crisp'],
  ];
  const index = Math.min(Math.floor(durationSeconds / 4), presets.length - 1);
  return presets[index];
}

async function loadProfileFromServer() {
  try {
    const response = await fetch(`${API_BASE}/profile`);
    if (!response.ok) {
      throw new Error('Profile request failed');
    }

    const profile = await response.json();
    state.profile = { ...state.profile, ...profile };
    renderProfile();
    setStatus('Profile loaded from the server.');
  } catch (error) {
    console.error(error);
    renderProfile();
    setStatus('No saved profile found yet.');
  }
}

async function saveProfileToServer() {
  const payload = {
    name: profileNameInput.value || 'My Voice',
    pitch: Number(pitchSlider.value),
    rate: Number(rateSlider.value),
    duration: Number(state.profile.duration || 0),
    tags: state.profile.tags || ['Warm', 'Conversational', 'Balanced'],
    sampleUrl: state.profile.sampleUrl || '',
  };

  try {
    const response = await fetch(`${API_BASE}/profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('Save failed');
    }

    state.profile = payload;
    renderProfile();
    setStatus(`Saved ${payload.name}'s voice profile.`);
  } catch (error) {
    console.error(error);
    setStatus('Profile save failed.');
  }
}

async function startRecording() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    setStatus('Microphone recording is not supported in this browser.');
    return;
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const url = URL.createObjectURL(blob);
      const duration = Number((blob.size / 1000).toFixed(2));

      state.profile.sampleUrl = url;
      state.profile.duration = duration;
      state.profile.tags = analyzeVoiceProfile(duration);
      state.profile.name = profileNameInput.value || 'My Voice';
      state.profile.pitch = Number(pitchSlider.value);
      state.profile.rate = Number(rateSlider.value);

      renderProfile();
      setStatus('Voice sample captured and ready to save.');
      stopStream();
    };

    mediaRecorder.start();
    recordButton.classList.add('hidden');
    stopButton.classList.remove('hidden');
    setStatus('Recording... say a short phrase for 5-10 seconds.');
  } catch (error) {
    console.error(error);
    setStatus('Microphone access was denied. Please allow access and try again.');
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }

  recordButton.classList.remove('hidden');
  stopButton.classList.add('hidden');
}

function stopStream() {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
}

function handleUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const url = URL.createObjectURL(file);
  const tempAudio = new Audio(url);

  tempAudio.onloadedmetadata = () => {
    state.profile.sampleUrl = url;
    state.profile.duration = tempAudio.duration || 0;
    state.profile.tags = analyzeVoiceProfile(state.profile.duration);
    state.profile.name = profileNameInput.value || 'Imported Voice';
    state.profile.pitch = Number(pitchSlider.value);
    state.profile.rate = Number(rateSlider.value);

    renderProfile();
    setStatus('Reference audio loaded and stored.');
  };
}

async function generateClone() {
  const text = scriptInput.value.trim();
  if (!text) {
    setStatus('Add some text before generating the clone.');
    return;
  }

  if (!('speechSynthesis' in window)) {
    setStatus('Text-to-speech is not supported in this browser.');
    return;
  }

  const payload = {
    text,
    pitch: Number(pitchSlider.value),
    rate: Number(rateSlider.value),
  };

  try {
    await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    console.error(error);
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.pitch = Number(pitchSlider.value);
  utterance.rate = Number(rateSlider.value);
  utterance.volume = 1;

  const voices = window.speechSynthesis.getVoices();
  const preferredVoice = voices.find((voice) => voice.lang.startsWith('en')) || voices[0];
  if (preferredVoice) {
    utterance.voice = preferredVoice;
  }

  setStatus(`Generating clone for ${state.profile.name || 'your voice'}...`);
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);

  utterance.onend = () => {
    setStatus('Clone finished.');
  };
}

recordButton.addEventListener('click', startRecording);
stopButton.addEventListener('click', stopRecording);
generateButton.addEventListener('click', generateClone);
stopSpeechButton.addEventListener('click', () => {
  window.speechSynthesis.cancel();
  setStatus('Speech playback stopped.');
});

saveProfileButton.addEventListener('click', saveProfileToServer);
audioUploadInput.addEventListener('change', handleUpload);
pitchSlider.addEventListener('input', () => {
  pitchValue.textContent = Number(pitchSlider.value).toFixed(1);
});
rateSlider.addEventListener('input', () => {
  rateValue.textContent = Number(rateSlider.value).toFixed(1);
});

loadProfileFromServer();
renderProfile();
setStatus('Ready to create a voice sample.');
