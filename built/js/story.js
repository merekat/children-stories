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
        const thumbWidth = 70; // Width of the thumb
        const availableWidth = sliderWidth - thumbWidth;
        const percent = (value - 1) / 3;
        const leftPosition = percent * availableWidth + thumbWidth / 2;

        childAgeThumb.css('left', `calc(${leftPosition}px - 35px)`);
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