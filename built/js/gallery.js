document.addEventListener('DOMContentLoaded', function () {
    fetch('/built/config/story.json')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('gallery-container');
            const loadMoreButton = document.getElementById('load-more');
            let currentIndex = 0;
            const batchSize = 6;

            // Function to shuffle the array
            function shuffleArray(array) {
                for (let i = array.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [array[i], array[j]] = [array[j], array[i]];
                }
                return array;
            }

            // Shuffle the data array
            const shuffledData = shuffleArray([...data]);

            // Function to load a batch of stories
            function loadStories() {
                const nextBatch = shuffledData.slice(currentIndex, currentIndex + batchSize);
                nextBatch.forEach(story => {
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

                currentIndex += batchSize;

                // Hide the load more button if all stories are loaded
                if (currentIndex >= shuffledData.length) {
                    loadMoreButton.style.display = 'none';
                }
            }

            // Initial load
            loadStories();

            // Load more stories on button click
            loadMoreButton.addEventListener('click', loadStories);
        })
        .catch(error => console.error('Error loading stories:', error));
});