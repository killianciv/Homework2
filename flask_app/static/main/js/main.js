
const feedbackSideButton = document.querySelector('.feedback_side_button');
const poppedUpFeedbackForm = document.querySelector('.invis_feedback_form');

// Function to open (unhide) the dropdown if clicking inside the tab
function openCloseFeedback(event) {
    if (
        feedbackSideButton.contains(event.target)
    ) {
        // Default class is mobile_dropdown. When clicked, alternate between
        //   default class and expanded_mobile_dropdown.
        poppedUpFeedbackForm.classList.toggle("popped_up_feedback_form");
        // poppedUpFeedbackForm.style.display = "flex";
    }
}
// Listen for clicks anywhere on the document
document.addEventListener("click", openCloseFeedback);


//
// Making the feedback box act how I want it to
//
const maxLength = 250;  // Max length of input
// Always update the text area's characters remaining
function updateCharCount() {
    const textarea = document.getElementById("comment");
    const charCount = document.getElementById("charCount");
    const remaining = maxLength - textarea.value.length;
    charCount.textContent = remaining + " characters remaining";
    // If the length exceeds maxLength, trim the text
    if (textarea.value.length > maxLength) {
        textarea.value = textarea.value.substring(0, maxLength); // Trims the input if exceeded
    }
}
// Prevent input from going beyond 250 characters
document.getElementById("comment").addEventListener("input", function(event) {
    const inputField = event.target;
    // If the length exceeds maxLength, trim the text
    if (inputField.value.length > maxLength) {
        inputField.value = inputField.value.substring(0, maxLength);
    }
    // Update character count
    updateCharCount();
});
// Handle paste event: restrict pasted text to remaining space
document.getElementById("comment").addEventListener("paste", function(event) {
    const inputField = event.target;
    const currentLength = inputField.value.length;
    // Calculate remaining space
    const remainingSpace = maxLength - currentLength;
    // Get the pasted text
    const pastedText = event.clipboardData.getData("text");
    // If the pasted text exceeds the remaining space, trim it
    if (pastedText.length > remainingSpace) {
        event.preventDefault(); // Prevent the paste
        inputField.value += pastedText.substring(0, remainingSpace); // Add only the allowed part
    } else {
        // If the paste is within the remaining space, allow it
        inputField.value += pastedText;
    }
    // Update the character count after pasting
    updateCharCount();
});
// Define keys to block. Otherwise, 'Tab' is printed in the text area
const blockedKeys = ['Tab', 'CapsLock', 'Meta', 'Escape', 'Enter', 'Shift',
    'Shift', 'Control', 'Alt'];
document.getElementById("comment").addEventListener("keydown", function(event) {
    const inputField = event.target;
    const key = event.key;
    // Allow arrow keys for navigation and Delete for deleting (don't block them)
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Backspace'].includes(key)) {
        return; // Allow navigation without preventing the default behavior
    }
    // Prevent default action for blocked keys
    if (blockedKeys.includes(key)) {
        event.preventDefault();
    }
});
// Handle text selection and deletion
document.getElementById("comment").addEventListener("input", function(event) {
    const inputField = event.target;
    const selectionStart = inputField.selectionStart;
    const selectionEnd = inputField.selectionEnd;
    // If text is selected and a key is pressed, replace the selected text
    if (selectionStart !== selectionEnd) {
        const selectedText = inputField.value.substring(selectionStart, selectionEnd);
        inputField.value = inputField.value.replace(selectedText, '');
    }
});

