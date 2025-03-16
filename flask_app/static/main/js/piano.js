
// As soon as the DOM loads, this whole function runs. It binds a lot of
//   different functions to a lot of different things and events
document.addEventListener("DOMContentLoaded",
    function () {

        // Defining a JSON Object (a dictionary) that maps the KeyCode from keypress events
        //   to the sound to play. We pass these URLs to an audio constructor in JS.
        const sound = {
            65: "http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
            87: "http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
            83: "http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
            69: "http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
            68: "http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
            70: "http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
            84: "http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
            71: "http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
            89: "http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
            72: "http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
            85: "http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
            74: "http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
            75: "http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
            79: "http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
            76: "http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
            80: "http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
            186: "http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"
        };

        // Awakening variables
        let keySequence = "";  // Track the last 8 keys pressed
        const targetSequence = "weseeyou";
        let isAwakened = false;

        // Function (used later) to play sound for the given key (on the keyboard)
        function playSound(key) {
            if (isAwakened) return;  // Do not play if he is awakened

            const upperKey = key.toUpperCase(); // Normalize key to uppercase
            let keyCode = upperKey.charCodeAt(0); // Get ASCII code
            if (upperKey === ";") {
                // Special case for semicolon or else the key doesn't work
                keyCode = 186; // The keyCode for semicolon
            }

            if (!sound[keyCode]) return;  // Ignore invalid keys

            const audio = new Audio(sound[keyCode]);
            audio.play();  // Used a JS audio constructor

            // Find the corresponding key element on the page (the element with data-key="A")
            const keyElement = document.querySelector(`[data-key="${upperKey}"]`);
            if (keyElement) {  // Animate the pressed key
                keyElement.classList.add("playing");
                setTimeout(() => keyElement.classList.remove("playing"), 150);
            }
        }

        // Binds keydown events to this function. On all future keydown events,
        //   if he is not awakened, update the sequence and call playSound()
        document.addEventListener("keydown", (event) => {
            if (isAwakened) return; // Disable input after awakening

            // If the user is typing in a Feedback box, do not make piano sounds
            const activeElement = document.activeElement;  // Currently focused (active) element
            // Check if the active element is an input or textarea. If it is, no more code runs.
            if (activeElement && (activeElement.tagName === "INPUT" || activeElement.tagName === "TEXTAREA")) {
                return; // Do nothing if the user is typing
            }

            // Ignore Shift, Enter, Tab, Option, Arrow keys, and other non-letter keys BEFORE calling
            //   playSound(). Old way: if (event.key === "Shift" || event.key === ...) { }
            const ignoredKeys = ["Shift", "Enter", "Tab",
                "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown",
                "Option", "Meta" ];  // "Meta" is Mac's Command key
            // If the key is in the ignoredKeys array, do nothing
            if (ignoredKeys.includes(event.key)) {
                return;
            }

            // Store the last 8 characters from key presses
            const key = event.key; // Get the key pressed
            keySequence += key.toLowerCase(); // Update key sequence
            keySequence = keySequence.slice(-targetSequence.length);
            if (keySequence === targetSequence) {
                awakenGreatOldOne();
            } else {
                playSound(key);
            }
        });

        // Find all .white-key's and all .black-key's, loop through and add a click
        //  event listener to each. So now when clicked, it calls playSound(its data-key).
        document.querySelectorAll(".white-key, .black-key").forEach(key => {
            key.addEventListener("click", (event) => {
                if (isAwakened) return;

                // Get the data-key, convert to uppercase for consistency
                const keyValue = key.getAttribute("data-key").toUpperCase(); // Get key from data-key
                keySequence += keyValue.toLowerCase(); // Update key sequence
                keySequence = keySequence.slice(-targetSequence.length);
                if (keySequence === targetSequence) {
                    awakenGreatOldOne();
                } else {
                    playSound(keyValue);
                }
            });
        });

        function awakenGreatOldOne() {
            isAwakened = true;  // To prevent future sound plays

            // Hide the piano
            const pianoElement = document.querySelector(".piano");
            pianoElement.style.transition = "opacity 1.5s";  // So when we change opacity, the change
                        // will be applied smoothly over 1.5s, fading the piano out over 2 seconds
            pianoElement.style.opacity = "0";  // Start fading out
            // After 2 seconds, hide the piano element from the layout (remove it)
            setTimeout(() => {
                pianoElement.style.display = "none";  // Remove from the layout after fade-out
            }, 1500);  // This code runs 1.5 seconds after awakenGreatOldOne is called
                               // (after the transition (fade-out) completes)

            // Fade in the Great Old One after 1.5 seconds
            const greatOne = document.querySelector(".asleep");
            setTimeout(() => {
                greatOne.className = "awoken";  // Change class to show the image
                // Set opacity to 0 first, then apply transition, and finally change opacity to 1
                greatOne.style.opacity = "0";  // Ensure it's initially hidden
                greatOne.style.transition = "opacity 1.5s";  // Apply the 1.5-second transition for fading in
                // Start the fade-in by setting opacity to 1 after applying the transition
                setTimeout(() => {
                    greatOne.style.opacity = "1";  // Fade in the image
                }, 50);  // Small delay to ensure transition is set before changing opacity
            }, 1500);  // All this happens after 1.5 seconds, which is right after the
                               // piano is fully faded out

            // Play creepy audio
            const creepyAudio = new Audio("https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1");
            creepyAudio.play();

            // // Scroll to the top of the Great Old One (after 3 seconds to prevent reload jumps)
            // setTimeout(() => {
            //     // Calculate some_vh from the top of the document (not relative to the current scroll position)
            //     const scrollPosition = window.innerHeight * 0.3;  // % of the viewport height
            //     window.scrollTo({
            //         top: scrollPosition,
            //         behavior: 'smooth' // Smooth scroll
            //     });
            // }, 2500);
        }
});

// While the mouse hovers over a key div, all key letters must become
//   visible, using a JS mousehover.
const allPianoKeys = document.querySelector('.keys')
const keyLabels = document.querySelectorAll('.keys h1');  // However far nested
// Function to show all key labels
allPianoKeys.addEventListener("mouseover", () => {
    keyLabels.forEach(label => label.style.display = "inline");
});
// Function to hide all key labels
allPianoKeys.addEventListener("mouseout", () => {
    keyLabels.forEach(label => label.style.display = "none");
});

