const STORAGE_KEY = 'voiceclone-profile';

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
let currentProfile = loadProfile();

function setStatus(message) {
  statusText.textContent = message;
}

function loadProfile() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) {
    return {
      name: 'My Voice',
      pitch: 1.0,
      rate: 1.0,
      duration: 0,
      tags: ['Warm', 'Conversational', 'Balanced'],
      sampleUrl: '',
    };
  }

  try {
    return JSON.parse(saved);
  } catch (error) {
    console.error('Failed to parse saved profile:', error);
    return {
      name: 'My Voice',
      pitch: 1.0,
      rate: 1.0,
      duration: 0,
      tags: ['Warm', 'Conversational', 'Balanced'],
      sampleUrl: '',
    };
  }
}

function saveProfileToStorage(profile) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
}

function syncProfileToForm() {
  profileNameInput.value = currentProfile.name || 'My Voice';
  pitchSlider.value = currentProfile.pitch || 1.0;
  rateSlider.value = currentProfile.rate || 1.0;
  pitchValue.textContent = Number(currentProfile.pitch || 1.0).toFixed(1);
  rateValue.textContent = Number(currentProfile.rate || 1.0).toFixed(1);
  durationValue.textContent = `${Number(currentProfile.duration || 0).toFixed(1)}s`;

  styleTags.innerHTML = '';
  (currentProfile.tags || ['Warm', 'Conversational', 'Balanced']).forEach((tag) => {
    const item = document.createElement('li');
    item.textContent = tag;
    styleTags.appendChild(item);
  });

  if (currentProfile.sampleUrl) {
    audioPreview.src = currentProfile.sampleUrl;
    audioPreview.classList.remove('hidden');
    sampleSummary.textContent = `${Number(currentProfile.duration || 0).toFixed(1)}s sample`;
  } else {
    audioPreview.classList.add('hidden');
    sampleSummary.textContent = 'No sample yet';
  }
}

function analyzeVoiceProfile(durationSeconds) {
  const warm = ['Warm', 'Conversational', 'Balanced'];
  const crisp = ['Crisp', 'Focused', 'Clear'];
  const energetic = ['Energetic', 'Bright', 'Confident'];

  const presets = [warm, crisp, energetic];
  const index = Math.min(Math.floor(durationSeconds / 4), presets.length - 1);

  return presets[index];
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

      currentProfile.sampleUrl = url;
      currentProfile.duration = Number((blob.size / 1000).toFixed(2));
      currentProfile.tags = analyzeVoiceProfile(currentProfile.duration);
      currentProfile.name = profileNameInput.value || 'My Voice';
      currentProfile.pitch = Number(pitchSlider.value);
      currentProfile.rate = Number(rateSlider.value);

      audioPreview.src = url;
      audioPreview.classList.remove('hidden');
      sampleSummary.textContent = `${currentProfile.duration.toFixed(1)}s sample`;
      durationValue.textContent = `${currentProfile.duration.toFixed(1)}s`;
      syncProfileToForm();
      saveProfileToStorage(currentProfile);
      setStatus('Voice sample captured and saved.');
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

function saveProfile() {
  currentProfile.name = profileNameInput.value || 'My Voice';
  currentProfile.pitch = Number(pitchSlider.value);
  currentProfile.rate = Number(rateSlider.value);

  if (!currentProfile.tags || currentProfile.tags.length === 0) {
    currentProfile.tags = ['Warm', 'Conversational', 'Balanced'];
  }

  saveProfileToStorage(currentProfile);
  syncProfileToForm();
  setStatus(`Saved ${currentProfile.name}'s voice profile.`);
}

function handleUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;

  const url = URL.createObjectURL(file);
  const audio = new Audio(url);

  audio.onloadedmetadata = () => {
    currentProfile.sampleUrl = url;
    currentProfile.duration = audio.duration;
    currentProfile.name = profileNameInput.value || 'Imported Voice';
    currentProfile.tags = analyzeVoiceProfile(audio.duration);
    currentProfile.pitch = Number(pitchSlider.value);
    currentProfile.rate = Number(rateSlider.value);

    audioPreview.src = url;
    audioPreview.classList.remove('hidden');
    sampleSummary.textContent = `${audio.duration.toFixed(1)}s sample`;
    durationValue.textContent = `${audio.duration.toFixed(1)}s`;
    syncProfileToForm();
    saveProfileToStorage(currentProfile);
    setStatus('Reference audio loaded and profile updated.');
  };
}

function generateClone() {
  const text = scriptInput.value.trim();
  if (!text) {
    setStatus('Add some text before generating the clone.');
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

  setStatus(`Generating cloned audio using ${currentProfile.name || 'your'} profile...`);
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

saveProfileButton.addEventListener('click', saveProfile);

audioUploadInput.addEventListener('change', handleUpload);
pitchSlider.addEventListener('input', () => {
  pitchValue.textContent = Number(pitchSlider.value).toFixed(1);
});
rateSlider.addEventListener('input', () => {
  rateValue.textContent = Number(rateSlider.value).toFixed(1);
});

if ('speechSynthesis' in window) {
  window.speechSynthesis.onvoiceschanged = () => { 
    // no-op: ensures voices are loaded when available
  };
}

syncProfileToForm();
setStatus('Ready to create a voice sample.');
