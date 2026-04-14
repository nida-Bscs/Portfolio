function scrollToSection(id) {
  document.getElementById(id).scrollIntoView({
    behavior: "smooth"
  });
}

/* Mobile menu */
function toggleMenu() {
  document.getElementById("nav").classList.toggle("active");
}

/* Dark / Light mode */
function toggleMode() {
  document.body.classList.toggle("light");
}

/* Contact */
function sendMessage(e) {
  e.preventDefault();
  alert("Message sent successfully!");
}

/* Scroll reveal animation */
window.addEventListener("scroll", () => {
  let reveals = document.querySelectorAll(".reveal");

  reveals.forEach(el => {
    let top = el.getBoundingClientRect().top;
    if (top < window.innerHeight - 100) {
      el.classList.add("active");
    }
  });
});