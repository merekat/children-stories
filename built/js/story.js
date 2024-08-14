$(document).ready(function () {
    // Duration Slider elements
    const durationSlider = $('#storyLength');
    const durationSliderThumb = durationSlider.siblings('.slider-thumb');
    const durationSliderValue = $('#sliderValue');
    const durationOptions = [2, 5, 10, 15, 20];

    // Child Age Slider elements
    const childAgeSlider = $('#childAge');
    const childAgeThumb = childAgeSlider.siblings('.slider-thumb');
    const childAgeOptions = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

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
        const nearestValue = childAgeOptions.reduce((prev, curr) => {
            return (Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev);
        });
        childAgeSlider.val(nearestValue);
        const percent = (nearestValue - childAgeSlider.attr('min')) / (childAgeSlider.attr('max') - childAgeSlider.attr('min')) * 100;
        childAgeThumb.css('left', `calc(${percent}%)`);
        childAgeThumb.text(nearestValue); // Display the value on the thumb
    }

    childAgeSlider.on('input', updateChildAgeSlider);
    childAgeSlider.val(4);
    updateChildAgeSlider();

    const speakerSelect = $('#speakerSelect');
    const newSpeakerSection = $('#newSpeakerSection');
    const uploadSection = $('#uploadSection .input-group');
    const recordingSection = $('#recordingSection .input-group');

    speakerSelect.on('change', function () {
        if (speakerSelect.val() === "new") {
            newSpeakerSection.show();
            uploadSection.show();
            recordingSection.show();
        } else {
            newSpeakerSection.hide();
            uploadSection.hide();
            recordingSection.hide();
        }
    });

});