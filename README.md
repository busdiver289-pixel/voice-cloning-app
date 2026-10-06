const STORAGE_KEY = 'personal-voice-lab-profiles';

const state = {
  profileId: 'default',
  profile: {
    id: 'default',
    name: 'My Voice',
    notes: '',
    pitch: 1.0,
    rate: 1.0,
    duration: 0,
    tags: ['Warm', 'Conversational', 'Balanced'],
    sampleUrl: '',
  },
  library: [],
};

const profileNameInput = document.getElementById('profileName');
const notesInput = document.getElementById('notesInput');
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
const exportProfileButton = document.getElementById('exportProfileButton');
const downloadAudioButton = document.getElementById('downloadAudioButton');
const profileList = document.getElementById('profileList');
const newProfileButton = document.getElementById('newProfileButton');

let mediaRecorder;
let audioChunks = [];
let stream;

function setStatus(message) {
  statusText.textContent = message;
}

function saveLocalLibrary() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.library));
}

function readLocalLibrary() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) {
    return [createDefaultProfile()];
  }
  try {
    const parsed = JSON.parse(saved);
    return Array.isArray(parsed) && parsed.length ? parsed : [createDefaultProfile()];
  } catch (error) {
    console.error(error);
    return [createDefaultProfile()];
  }
}

function createDefaultProfile() {
  return {
    id: 'default',
    name: 'My Voice',
    notes: 'Default personal profile',
    pitch: 1.0,
    rate: 1.0,
    duration: 0,
    tags: ['Warm', 'Conversational', 'Balanced'],
    sampleUrl: '',
  };
}

function renderProfileSummary() {
  profileNameInput.value = state.profile.name || 'My Voice';
  notesInput.value = state.profile.notes || '';
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

function renderLibrary() {
  profileList.innerHTML = '';

  state.library.forEach((profile) => {
    const row = document.createElement('div');
    row.className = 'profile-item';
    row.innerHTML = `
      <div>
        <strong>${profile.name}</strong>
        <div>${profile.tags?.join(', ') || 'Warm'}</div>
      </div>
      <button type="button">Use</button>
    `;

    const useButton = row.querySelector('button');
    useButton.addEventListener('click', () => {
      state.profile = { ...profile };
      state.profileId = profile.id;
      renderProfileSummary();
      setStatus(`Loaded ${profile.name}.`);
    });

    profileList.appendChild(row);
  });
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

function exportProfile() {
  const profile = {
    id: state.profileId || `profile-${Date.now()}`,
    name: profileNameInput.value || 'My Voice',
    notes: notesInput.value || '',
    pitch: Number(pitchSlider.value),
    rate: Number(rateSlider.value),
    duration: Number(state.profile.duration || 0),
    tags: state.profile.tags || ['Warm', 'Conversational', 'Balanced'],
    sampleUrl: state.profile.sampleUrl || '',
    exportedAt: new Date().toISOString(),
  };

  const blob = new Blob([JSON.stringify(profile, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${profile.name.toLowerCase().replace(/\s+/g, '-') || 'voice-profile'}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
  setStatus(`Exported ${profile.name} profile JSON.`);
}

function downloadSampleAudio() {
  if (!state.profile.sampleUrl) {
    setStatus('No sample audio is available to download yet.');
    return;
  }

  const link = document.createElement('a');
  link.href = state.profile.sampleUrl;
  link.download = `${(state.profile.name || 'voice-sample').toLowerCase().replace(/\s+/g, '-')}.webm`;
  link.click();
  setStatus('Sample audio download started.');
}

function saveProfile() {
  const profile = {
    id: state.profileId || `profile-${Date.now()}`,
    name: profileNameInput.value || 'My Voice',
    notes: notesInput.value || '',
    pitch: Number(pitchSlider.value),
    rate: Number(rateSlider.value),
    duration: Number(state.profile.duration || 0),
    tags: state.profile.tags || ['Warm', 'Conversational', 'Balanced'],
    sampleUrl: state.profile.sampleUrl || '',
  };

  state.profile = profile;
  state.profileId = profile.id;

  const existingIndex = state.library.findIndex((item) => item.id === profile.id);
  if (existingIndex >= 0) {
    state.library[existingIndex] = profile;
  } else {
    state.library.push(profile);
  }

  saveLocalLibrary();
  renderLibrary();
  renderProfileSummary();
  setStatus(`Saved ${profile.name} locally.`);
}

function newProfile() {
  const fresh = createDefaultProfile();
  fresh.id = `profile-${Date.now()}`;
  fresh.name = 'New Voice';
  state.profile = fresh;
  state.profileId = fresh.id;
  renderProfileSummary();
  setStatus('Started a new local profile.');
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

      renderProfileSummary();
      setStatus('Voice sample captured locally.');
      stopStream();
    };

    mediaRecorder.start();
    recordButton.classList.add('hidden');
    stopButton.classList.remove('hidden');
    setStatus('Recording... speak for a few seconds.');
  } catch (error) {
    console.error(error);
    setStatus('Microphone access was denied.');
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

    renderProfileSummary();
    setStatus('Reference audio loaded.');
  };
}

function generatePreview() {
  const text = scriptInput.value.trim();
  if (!text) {
    setStatus('Add text before generating the preview.');
    return;
  }

  if (!('speechSynthesis' in window)) {
    setStatus('Text-to-speech is not supported in this browser.');
    return;
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

  setStatus(`Generating preview for ${state.profile.name || 'your voice'}...`);
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);

  utterance.onend = () => {
    setStatus('Preview finished.');
  };
}

recordButton.addEventListener('click', startRecording);
stopButton.addEventListener('click', stopRecording);

generateButton.addEventListener('click', generatePreview);
stopSpeechButton.addEventListener('click', () => {
  window.speechSynthesis.cancel();
  setStatus('Playback stopped.');
});

saveProfileButton.addEventListener('click', saveProfile);
exportProfileButton.addEventListener('click', exportProfile);
downloadAudioButton.addEventListener('click', downloadSampleAudio);
newProfileButton.addEventListener('click', newProfile);
audioUploadInput.addEventListener('change', handleUpload);

pitchSlider.addEventListener('input', () => {
  pitchValue.textContent = Number(pitchSlider.value).toFixed(1);
});

rateSlider.addEventListener('input', () => {
  rateValue.textContent = Number(rateSlider.value).toFixed(1);
});

state.library = readLocalLibrary();
const current = state.library[0] || createDefaultProfile();
state.profile = { ...current };
state.profileId = current.id || 'default';
renderLibrary();
renderProfileSummary();
setStatus('Ready.');
