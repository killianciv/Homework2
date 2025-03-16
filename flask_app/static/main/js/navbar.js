
// Select the menu bar image from the DOM
const menuBarImage = document.querySelector('.mobile_menu_bar_link');
// Select the visible div.mobile_dropdown from the DOM
const mobileNavbar = document.querySelector('.mobile_dropdown');

// Toggles the visibility of the mobile navbar
function dropDown() {
    // Default class is mobile_dropdown. When clicked, alternate between
    //   default class and expanded_mobile_dropdown.
    mobileNavbar.classList.toggle("expanded_mobile_dropdown");
}
// When we click on the menu bar image, call dropDown()
menuBarImage.addEventListener("click", dropDown);

// Closes the dropped-down mobile menu when screen goes above 650px
// Menu will have already disappeared but I also need to remove the links
function closeMenuOnResize() {
    if (window.innerWidth > 650) {
        // Cannot just toggle because that will open it if the mobile menu was
        //   closed before the screen was enlarged
        mobileNavbar.classList.remove("expanded_mobile_dropdown"); // Force hide
    }
}
// Attach event listener to window resize
window.addEventListener("resize", closeMenuOnResize);


// Added during Homework 2:
// Function to close the dropdown if clicking outside of it
function closeDropdown(event) {
    if (
        !mobileNavbar.contains(event.target) &&
        !menuBarImage.contains(event.target)
    ) {
        mobileNavbar.classList.remove("expanded_mobile_dropdown");
    }
}
// Listen for clicks anywhere on the document
document.addEventListener("click", closeDropdown);
