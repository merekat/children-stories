document.addEventListener('DOMContentLoaded', function () {
    const originalTitle = storyData.originalTitle;
    const sanitizedTitle = storyData.sanitizedTitle;
    const language = storyData.language;
    const existingSpeakersSelect = document.getElementById('existingSpeakers');
    const allSpeakersSelect = document.getElementById('allSpeakers');
    const generateButton = document.getElementById('generateButton');
    const generationStatus = document.getElementById('generationStatus');
    const backendUrl = 'http://localhost:5000'; // Adjust this if your backend URL is different

    let existingSpeakers = [];
    let allSpeakers = [];

    function fetchSpeakers() {
        const title = storyData.sanitizedTitle;
        fetch(`/get-story-speakers?title=${encodeURIComponent(title)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    existingSpeakers = data.existing_speakers;
                    allSpeakers = data.all_speakers;

                    // Ensure "standard" is always in allSpeakers
                    if (!allSpeakers.includes("standard")) {
                        allSpeakers.push("standard");
                    }

                    populateExistingSpeakers();
                    populateAllSpeakers();
                } else {
                    console.error('Error fetching speakers:', data.error);
                    existingSpeakers = [];
                    allSpeakers = ['standard'];
                    populateExistingSpeakers();
                    populateAllSpeakers();
                }
            })
            .catch(error => {
                console.error('Error fetching speakers:', error);
                existingSpeakers = [];
                allSpeakers = ['standard'];
                populateExistingSpeakers();
                populateAllSpeakers();
            });
    }

    function populateExistingSpeakers() {
        existingSpeakersSelect.innerHTML = '';
        existingSpeakers.forEach(speaker => {
            const option = document.createElement('option');
            option.value = speaker;
            option.textContent = speaker;
            existingSpeakersSelect.appendChild(option);
        });
    }

    function populateAllSpeakers() {
        allSpeakersSelect.innerHTML = '<option value=""></option>';

        // Create an array to hold the speakers we'll add to the select
        let speakersToAdd = allSpeakers.filter(speaker => !existingSpeakers.includes(speaker));

        // If "standard" is in speakersToAdd, remove it so we can add it separately
        const standardIndex = speakersToAdd.indexOf("standard");
        if (standardIndex > -1) {
            speakersToAdd.splice(standardIndex, 1);
        }

        // Add "standard" as the second option if it's not in existingSpeakers
        if (!existingSpeakers.includes("standard")) {
            const standardOption = document.createElement('option');
            standardOption.value = "standard";
            standardOption.textContent = "standard";
            allSpeakersSelect.appendChild(standardOption);
        }

        // Add the rest of the speakers
        speakersToAdd.forEach(speaker => {
            const option = document.createElement('option');
            option.value = speaker;
            option.textContent = speaker;
            allSpeakersSelect.appendChild(option);
        });
    }

    // Function to format the title
    function formatTitle(title) {
        return title.replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    // Set the formatted title
    document.querySelector('h2').textContent = formatTitle(originalTitle);

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

    fetchSpeakers();
    setupAudioPlayback();

    existingSpeakersSelect.addEventListener('change', function () {
        updateAudioSources(this.value);
    });

    allSpeakersSelect.addEventListener('change', function () {
        generateButton.disabled = !this.value;
    });

    function fetchLatestSpeakerData() {
        return fetch(`/get-story-speakers?title=${encodeURIComponent(sanitizedTitle)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    existingSpeakers = data.existing_speakers;
                    allSpeakers = data.all_speakers;
                    populateExistingSpeakers();
                    populateAllSpeakers();
                } else {
                    throw new Error(data.error || "Error fetching speakers");
                }
            });
    }

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
                    // Update audio sources
                    updateAudioSources(speaker);

                    // Fetch latest speaker data
                    return fetchLatestSpeakerData();
                } else {
                    throw new Error(data.message || "Error generating audio");
                }
            })
            .then(() => {
                // Update the first select with the new speaker
                if (!existingSpeakers.includes(speaker)) {
                    existingSpeakers.push(speaker);
                    const option = document.createElement('option');
                    option.value = speaker;
                    option.textContent = speaker;
                    existingSpeakersSelect.appendChild(option);
                }
                existingSpeakersSelect.value = speaker;

                // Update the second select
                populateAllSpeakers(); // This will recreate the options based on the updated speaker lists

                // Show success message
                generationStatus.textContent = "Audio generated successfully!";
            })
            .catch(error => {
                console.error('Error:', error);
                generationStatus.textContent = "An error occurred while generating audio: " + error.message;
            })
            .finally(() => {
                generateButton.disabled = false;
            });
    });

});