document.addEventListener('DOMContentLoaded', function () {
    fetch('/built/config/story.json')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('gallery-container');

            // Function to shuffle the array
            function shuffleArray(array) {
                for (let i = array.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [array[i], array[j]] = [array[j], array[i]];
                }
                return array;
            }

            // Shuffle the data array
            const shuffledData = shuffleArray([...data]); // Create a copy before shuffling
            console.log('Shuffled Stories:', shuffledData); // Debugging line

            shuffledData.forEach(story => {
                const storyLink = document.createElement('a');
                const storyDiv = document.createElement('div');
                storyDiv.className = 'story';

                const title = story.title.replace(/_/g, ' ').toLowerCase();
                const formattedTitle = title.charAt(0).toUpperCase() + title.slice(1);
                const imgSrc = `/built/static/image/${story.title}_cover.png`;
                const defaultImgSrc = '/built/static/image/standard_cover.png';

                const img = new Image();
                img.onload = function () {
                    storyDiv.style.backgroundImage = `url('${imgSrc}')`;
                };
                img.onerror = function () {
                    storyDiv.style.backgroundImage = `url('${defaultImgSrc}')`;
                };
                img.src = imgSrc;

                const titleSpan = document.createElement('span');
                titleSpan.textContent = formattedTitle;

                storyDiv.appendChild(titleSpan);
                storyLink.appendChild(storyDiv);
                storyLink.href = `/built/static/story/${story.title}.html`;
                container.appendChild(storyLink);
            });
        })
        .catch(error => console.error('Error loading stories:', error));
});