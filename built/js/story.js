$(document).ready(function () {
    // Duration Slider elements
    const durationSlider = $('#storyLength');
    const durationSliderThumb = durationSlider.siblings('.slider-thumb');
    const durationSliderValue = $('#sliderValue');
    const durationOptions = [2, 5, 10, 15, 20];

    // Age Slider elements
    const childAgeSlider = $('#childAge');
    const childAgeThumb = childAgeSlider.siblings('.slider-thumb');
    const childAgeRanges = [{
            value: 1,
            text: "0 - 2 years"
        },
        {
            value: 2,
            text: "2 - 5 years"
        },
        {
            value: 3,
            text: "5 - 7 years"
        },
        {
            value: 4,
            text: "7 - 12 years"
        }
    ];

    // Duration Slider functionality
    function updateDurationSlider() {
        const value = parseInt(durationSlider.val());
        const nearestValue = durationOptions.reduce((prev, curr) => {
            return (Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev);
        });
        durationSlider.val(nearestValue);
        durationSliderValue.text(nearestValue);

        const percent = (nearestValue - durationSlider.attr('min')) / (durationSlider.attr('max')) * 100;
        durationSliderThumb.css('left', `calc(${percent}%)`);
    }

    durationSlider.on('input', updateDurationSlider);
    durationSlider.val(5);
    updateDurationSlider();

    const durationSliderContainer = durationSlider.parent();
    durationOptions.forEach(duration => {
        const percent = (duration - durationSlider.attr('min')) / (durationSlider.attr('max')) * 100;
        const label = $('<span></span>')
            .text(duration)
            .css({
                'user-select': 'none',
                'padding': '5px 6px',
                'position': 'absolute',
                'left': `calc(${percent}% -  1px)`,
                'bottom': '8px',
                'background': '#e7e7e6',
                'font-size': '12px',
                'line-height': '8px',
                'color': '#666',
                'transform': 'translate(12px, -2px)',
                'pointer-events': 'none'
            });
        durationSliderContainer.append(label);
    });

    // Child Age Slider functionality
    function updateChildAgeSlider() {
        const value = parseInt(childAgeSlider.val());
        const range = childAgeRanges.find(r => r.value === value);

        childAgeSlider.val(value);
        const sliderWidth = childAgeSlider.width();
        const thumbWidth = 80; // Width of the thumb
        const availableWidth = sliderWidth - thumbWidth;
        const percent = (value - 1) / 3;
        const leftPosition = percent * availableWidth + thumbWidth / 2;

        childAgeThumb.css('left', `calc(${leftPosition}px - 40px)`);
        childAgeThumb.text(range.text);
    }

    childAgeSlider.attr('min', 1);
    childAgeSlider.attr('max', 4);
    childAgeSlider.attr('step', 1);
    childAgeSlider.on('input', updateChildAgeSlider);
    childAgeSlider.val(2); // Set default to "2 - 5 years"
    updateChildAgeSlider();

    const speakerSelect = $('#speakerSelect');
    const newSpeakerSection = $('#newSpeakerSection');
    const uploadSection = $('#uploadSection .input-group');
    const recordingSection = $('#recordingSection .input-group');
    const startRecordButton = $('#startRecord');
    const stopRecordButton = $('#stopRecord');
    const readingExample = $('#readingExample');
    const audioPlayback = $('#audioPlayback');
    const generateStoryButton = $('#generateStoryButton');
    const content = $('#content');
    const speakerNameInput = $('#speakerName');
    const audioFileInput = $('#audioFileInput');

    const backendUrl = 'http://127.0.0.1:5000';

    let mediaRecorder;
    let audioChunks = [];

    // Initially hide all sections
    newSpeakerSection.hide();
    uploadSection.hide();
    recordingSection.hide();

    // Smooth scroll function
    $('#scrollToInterface').on('click', function (event) {
        event.preventDefault();
        $('html, body').animate({
            scrollTop: $('#interface').offset().top
        }, 500);
    });

    function loadSpeakers() {
        $.getJSON(`${backendUrl}/speaker`, function (data) {
            speakerSelect.empty().append(
                '<option value="new">Use your own Voice</option>'
            );

            // Add the "Standard" option and set it as selected
            speakerSelect.append('<option value="standard" selected>Standard</option>');

            if (data.speakers && data.speakers.length > 0) {
                data.speakers.forEach(function (speaker) {
                    if (speaker !== "Standard") { // Skip "Standard" if it's in the API response
                        speakerSelect.append($('<option></option>').val(speaker).text(speaker));
                    }
                });
            }
        });
    }

    loadSpeakers();

    speakerSelect.on('change', function () {
        if (speakerSelect.val() === "new") {
            newSpeakerSection.show();
            uploadSection.show();
            recordingSection.show();
            readingExample.show();
            audioPlayback.hide();
            startRecordButton.prop('disabled', false);
            stopRecordButton.prop('disabled', true);
            speakerNameInput.prop('disabled', false);
            audioFileInput.prop('disabled', false);
        } else {
            newSpeakerSection.hide();
            uploadSection.hide();
            recordingSection.hide();
            speakerNameInput.prop('disabled', true).val('');
            audioFileInput.prop('disabled', true);
            startRecordButton.prop('disabled', true);
        }
    });

    // Handle speaker name input
    speakerNameInput.on('input', function () {
        if (speakerNameInput.val().length > 0) {
            speakerSelect.val("new").prop('disabled', true);
        } else {
            speakerSelect.prop('disabled', false);
        }
    });

    // Recording functionality
    startRecordButton.on('click', async function () {
        audioChunks = [];
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, {
                    type: 'audio/wav'
                });
                const audioUrl = URL.createObjectURL(audioBlob);
                audioPlayback.attr('src', audioUrl);
            };
            mediaRecorder.start();
            startRecordButton.prop('disabled', true);
            stopRecordButton.prop('disabled', false);
            readingExample.show();
            audioPlayback.hide();
        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Error accessing microphone. Please make sure you have granted permission.');
        }
    });

    stopRecordButton.on('click', function () {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            startRecordButton.prop('disabled', false);
            stopRecordButton.prop('disabled', true);
            readingExample.hide();
            audioPlayback.show();
        }
    });

    // Generate story
    generateStoryButton.on('click', function () {
        const selectedSpeaker = speakerSelect.val();
        const speakerName = speakerNameInput.val();
        const audioFile = audioFileInput[0].files[0];

        // Save child information
        saveChildInfo(childName, childAge, language);

        if (selectedSpeaker === "new") {
            if (!speakerName || (!audioFile && audioChunks.length === 0)) {
                alert('Please enter a speaker name and provide an audio file or recording.');
                return;
            }

            const formData = new FormData();
            formData.append('speakerName', speakerName);
            if (audioFile) {
                formData.append('audioFile', audioFile);
            } else if (audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, {
                    type: 'audio/wav'
                });
                formData.append('audioFile', audioBlob, 'recording.wav');
            }

            // Save audio and update speaker.json
            fetch(`${backendUrl}/save-audio`, {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Audio and speaker saved successfully!');
                        startStoryGeneration(speakerName);
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
        } else {
            // Use existing speaker
            startStoryGeneration(selectedSpeaker);
        }
    });

    function startStoryGeneration(speaker) {
        generateStoryButton.prop('disabled', true);
        content.empty();

        const topicInput = $('#storyTopic').length ? $('#storyTopic').val().trim() : '';
        const storyLengthMinutes = $('#storyLength').length ? parseInt($('#storyLength').val(), 10) : 5;
        const wordCount = storyLengthMinutes * 150;
        const mainCharacter = $('#storyMaincharacter').length ? $('#storyMaincharacter').val().trim() : '';
        const settingInput = $('#storySetting').val().trim();
        const userPrompt = $('#storyPrompt').length ? $('#storyPrompt').val().trim() : '';
        const languageCode = $('#language').length ? $('#language').val() : 'en';
        const languageName = $('#language').length ? $('#language option:selected').text() : 'English';
        const childAge = $('#childAge').length ? parseInt($('#childAge').val(), 10) : 2;

        // Collect selected moral lessons
        const selectedMoralLessons = [];
        $('input[name="moralLesson"]:checked').each(function () {
            selectedMoralLessons.push($(this).val());
        });

        $.ajax({
            url: `${backendUrl}/generate-story`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                topic: topicInput,
                child_age: childAge,
                word_count: wordCount,
                speaker: speaker,
                language_code: languageCode,
                language_name: languageName,
                main_character: mainCharacter,
                setting: settingInput,
                user_prompt: userPrompt,
                moral_lessons: selectedMoralLessons
            }),
            success: function (data) {
                if (data.success) {
                    content.html(`<h2>${data.title}</h2>`);
                    displayTextChunks(speaker, data.title);
                } else {
                    content.html('<p>Error generating story. Please try again.</p>');
                }
            },
            error: function () {
                content.html('<p>Error generating story. Please try again.</p>');
            },
            complete: function () {
                generateStoryButton.prop('disabled', false);
            }
        });
    }

    function displayTextChunks(speaker, title) {
        fetch(`${backendUrl}/process?speaker=${speaker}&title=${title}&generate_audio=false`)
            .then(response => response.json())
            .then(data => {
                // Create the content div 
                let contentDiv = $('#content');
                if (contentDiv.length === 0) {
                    contentDiv = $('<div id="content"></div>');
                    $('.button-container').after(contentDiv); // Insert after the button container
                }

                contentDiv.empty(); // Clear any existing content

                // Add the title
                const titleElement = $('<h2></h2>')
                    .addClass('story-title')
                    .text(title);
                contentDiv.append(titleElement);

                data.forEach((item, index) => {
                    const chunkDiv = $('<div></div>')
                        .addClass('chunk')
                        .attr('data-index', index)
                        .html(`<p>${item.text}</p>`);
                    contentDiv.append(chunkDiv);
                });

                // Show the content div
                contentDiv.show();

                // After displaying text, start generating audio
                generateAudioForChunks(speaker, title);
            })
            .catch(error => {
                console.error('Error fetching text chunks:', error);
                alert('An error occurred while processing the text. Please try again.');
            });
    }

    function generateAudioForChunks(speaker, title) {
        fetch(`${backendUrl}/process?speaker=${speaker}&title=${title}&generate_audio=true`)
            .then(response => response.json())
            .then(data => {
                const contentDiv = $('#content');
                data.forEach((item, index) => {
                    if (item.audio) {
                        const chunkDiv = contentDiv.find(`.chunk[data-index='${index}']`);
                        const audioPlayer = $('<audio></audio>')
                            .attr('src', `${backendUrl}${item.audio}`)
                            .hide();
                        const playButton = $('<button></button>')
                            .addClass('play-button')
                            .html('<i class="fas fa-play"></i>')
                            .on('click', function () {
                                const icon = $(this).find('i');
                                if (icon.hasClass('fa-play')) {
                                    audioPlayer[0].play();
                                    icon.removeClass('fa-play').addClass('fa-pause');
                                } else {
                                    audioPlayer[0].pause();
                                    icon.removeClass('fa-pause').addClass('fa-play');
                                }
                            });
                        chunkDiv.prepend(playButton);
                        chunkDiv.append(audioPlayer);

                        // Add event listener for when audio ends
                        audioPlayer[0].addEventListener('ended', function () {
                            playButton.find('i').removeClass('fa-pause').addClass('fa-play');
                        });

                        // Add autoplay with delay
                        if (index < data.length - 1) {
                            audioPlayer[0].addEventListener('ended', function () {
                                setTimeout(() => {
                                    const nextAudio = contentDiv.find(`.chunk[data-index='${index + 1}'] audio`)[0];
                                    const nextButton = contentDiv.find(`.chunk[data-index='${index + 1}'] .play-button i`);
                                    if (nextAudio) {
                                        nextAudio.play();
                                        nextButton.removeClass('fa-play').addClass('fa-pause');
                                    }
                                }, 1000); // 1 second delay
                            });
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Error generating audio:', error);
            });
    }

    function saveChildInfo(childName, childAge, language) {
        fetch(`${backendUrl}/save-child-info`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    childName: childName,
                    childAge: childAge,
                    language: language
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Child information saved successfully');
                } else {
                    console.error('Error saving child information:', data.error);
                }
            })
            .catch(error => {
                console.error('Error saving child information:', error);
            });
    }

});