let mediaRecorder;
let audioChunks = [];
let audioBlob;
let isRecording = false;

const startRecordButton = document.getElementById('startRecord');
const stopRecordButton = document.getElementById('stopRecord');
const audioPlayback = document.getElementById('audioPlayback');
const audioFileInput = document.getElementById('audioFileInput');
const saveSection = document.getElementById('saveSection');
const usernameInput = document.getElementById('username');
const saveAudioButton = document.getElementById('saveAudio');

startRecordButton.addEventListener('click', startRecording);
stopRecordButton.addEventListener('click', stopRecording);
audioFileInput.addEventListener('change', handleFileUpload);
saveAudioButton.addEventListener('click', saveAudio);

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({
        audio: true
    });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.addEventListener('dataavailable', event => {
        audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener('stop', () => {
        audioBlob = new Blob(audioChunks, {
            type: 'audio/wav'
        });
        const audioUrl = URL.createObjectURL(audioBlob);
        audioPlayback.src = audioUrl;
        audioPlayback.style.display = 'block';
        saveSection.style.display = 'block';
    });

    mediaRecorder.start();
    isRecording = true;
    startRecordButton.disabled = true;
    stopRecordButton.disabled = false;

    // Stop recording after 2 minutes
    setTimeout(() => {
        if (isRecording) {
            stopRecording();
        }
    }, 120000);
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    startRecordButton.disabled = false;
    stopRecordButton.disabled = true;
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        audioBlob = file;
        const audioUrl = URL.createObjectURL(file);
        audioPlayback.src = audioUrl;
        audioPlayback.style.display = 'block';
        saveSection.style.display = 'block';
    }
}

function saveAudio() {
    const username = usernameInput.value.trim();
    if (!username) {
        alert('Please enter a username');
        return;
    }

    const formData = new FormData();

    // If audioBlob is from a recorded audio
    if (audioBlob instanceof Blob) {
        formData.append('audio', audioBlob, `${username}.wav`);
    }
    // If audioBlob is from an uploaded file
    else if (audioBlob instanceof File) {
        formData.append('audio', audioBlob, audioBlob.name);
    } else {
        alert('No valid audio data');
        return;
    }

    fetch('http://localhost:5001/save-audio', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Audio saved successfully. Training model...');
                trainModel(username);
            } else {
                alert(`Error saving audio: ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Error saving audio: ${error}`);
        });
}

function trainModel(username) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes timeout

    fetch('http://localhost:5001/train-model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username
            }),
            signal: controller.signal
        })
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Model training started successfully. It may take a few minutes to complete.');
            } else {
                alert(`Error starting model training: ${data.error}`);
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error:', error);
            alert(`Error starting model training: ${error.message}`);
        });
}