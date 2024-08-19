document.addEventListener('DOMContentLoaded', function () {
    const originalTitle = storyData.originalTitle;
    const sanitizedTitle = storyData.sanitizedTitle;
    const language = storyData.language;
    const existingSpeakersSelect = document.getElementById('existingSpeakers');
    const allSpeakersSelect = document.getElementById('allSpeakers');
    const generateButton = document.getElementById('generateButton');
    const generationStatus = document.getElementById('generationStatus');
    const backendUrl = 'http://localhost:5000'; // Adjust this if your backend URL is different

    const speakerData = document.getElementById('speakerData');
    const existingSpeakersJson = speakerData.getAttribute('data-existing-speakers');
    const allSpeakersJson = speakerData.getAttribute('data-all-speakers');

    let existingSpeakers, allSpeakers;
    try {
        existingSpeakers = JSON.parse(existingSpeakersJson);
        allSpeakers = JSON.parse(allSpeakersJson);
    } catch (error) {
        console.error("Error parsing JSON:", error);
        existingSpeakers = [];
        allSpeakers = [];
    }

    // Set the title
    document.querySelector('h1').textContent = originalTitle;

    function populateExistingSpeakers(speakers) {
        existingSpeakersSelect.innerHTML = '';
        speakers.forEach(speaker => {
            const option = document.createElement('option');
            option.value = speaker;
            option.textContent = speaker;
            existingSpeakersSelect.appendChild(option);
        });
    }

    function populateAllSpeakers(allSpeakers, existingSpeakers) {
        allSpeakersSelect.innerHTML = '<option value="">Select a new speaker</option>';
        allSpeakers.forEach(speaker => {
            if (!existingSpeakers.includes(speaker)) {
                const option = document.createElement('option');
                option.value = speaker;
                option.textContent = speaker;
                allSpeakersSelect.appendChild(option);
            }
        });
    }

    function updateAudioSources(speaker) {
        const audioElements = document.querySelectorAll('audio');
        audioElements.forEach((audio, index) => {
            audio.src = `/built/static/audio/${speaker}_${language}_${sanitizedTitle}_${index + 1}.wav`;
        });
    }

    function setupAudioPlayback() {
        const chunks = document.querySelectorAll('.chunk');
        chunks.forEach((chunk, index) => {
            const playButton = chunk.querySelector('.play-button');
            const audio = chunk.querySelector('audio');
            const icon = playButton.querySelector('i');

            playButton.addEventListener('click', function () {
                if (audio.paused) {
                    audio.play();
                    icon.classList.replace('fa-play', 'fa-pause');
                } else {
                    audio.pause();
                    icon.classList.replace('fa-pause', 'fa-play');
                }
            });

            audio.addEventListener('ended', function () {
                icon.classList.replace('fa-pause', 'fa-play');
                if (index < chunks.length - 1) {
                    setTimeout(() => {
                        const nextChunk = chunks[index + 1];
                        const nextAudio = nextChunk.querySelector('audio');
                        const nextIcon = nextChunk.querySelector('.play-button i');
                        if (nextAudio && nextIcon) {
                            nextAudio.play();
                            nextIcon.classList.replace('fa-play', 'fa-pause');
                        }
                    }, 1000);
                }
            });
        });
    }

    populateExistingSpeakers(existingSpeakers);
    populateAllSpeakers(allSpeakers, existingSpeakers);

    if (existingSpeakers.length > 0) {
        existingSpeakersSelect.value = existingSpeakers[0];
        updateAudioSources(existingSpeakers[0]);
    }

    setupAudioPlayback();

    existingSpeakersSelect.addEventListener('change', function () {
        updateAudioSources(this.value);
    });

    allSpeakersSelect.addEventListener('change', function () {
        generateButton.disabled = !this.value;
    });

    generateButton.addEventListener('click', function () {
        const speaker = allSpeakersSelect.value;
        if (!speaker) return;

        generationStatus.textContent = "Generating audio...";
        generateButton.disabled = true;

        // Collect all text from chunks
        const fullText = Array.from(document.querySelectorAll('.chunk p'))
            .map(p => p.textContent)
            .join(' ');

    fetch(`${backendUrl}/generate_audio`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                speaker: speaker,
                language: language,
                title: sanitizedTitle,
                text: fullText
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                generationStatus.textContent = "Audio generated successfully!";
                updateAudioSources(speaker);
                // ... (rest of the success handling)
            } else {
                generationStatus.textContent = "Error generating audio: " + data.message;
            }
        })
            .catch(error => {
                console.error('Error:', error);
                generationStatus.textContent =
                    "An error occurred while generating audio: " +
                    error.message;
            })
            .finally(() => {
                generateButton.disabled = false;
            });
    });
});