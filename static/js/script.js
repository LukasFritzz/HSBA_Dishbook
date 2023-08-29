// Navigation Bar
let menu    = document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
};


// Index page load animation
const scrollItem = ScrollReveal ({
    distance: '65px',
    duration: 1800,
    delay:    1000,
    reset:    true
});

scrollItem.reveal('.main-text'  ,{delay:200, origin:'top'});
scrollItem.reveal('.main-img'   ,{delay:350, origin:'top'});
scrollItem.reveal('.icon'       ,{delay:400, origin:'left'});
scrollItem.reveal('.result-link',{delay:400, origin:'right'});


// Image preview index page 
function getImagePreview(event) {

  var container = document.getElementById("main-img"); 
  container.style.display = "block";

  var container = document.getElementById("map"); 
  container.style.display = "none";

  var file  = event.target.files[0];
  
  if (file && /\.(jpg|png|jpeg)$/i.test(file.name)) {
      var image         = URL.createObjectURL(file);
      let imageElement  = document.querySelector('.main-img img');
      imageElement.src  = image;
  }
};


// Login page input placeholder animation  
const inputs      = document.querySelectorAll(".input_field");

inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("activeInput");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("activeInput");
  });
});


// Login page login and sign up animation
const toggle_btn  = document.querySelectorAll(".toggle");
const main        = document.querySelector(".login_section");

toggle_btn.forEach((btn) => {
  btn.addEventListener("click", () => {
    main.classList.toggle("sign-up-mode");
  });
});


// Login page image slide show with buttons
if (window.location.pathname.includes('/login')) {
  const bullets     = document.querySelectorAll(".bullets span");
  const images      = document.querySelectorAll(".image");

  let currentSlide  = 1;
  let intervalId    = null;

  function changeSlide() {
    currentSlide = (currentSlide % images.length) + 1;
    updateSlide(currentSlide);
  }

  function updateSlide(index) {
    images.forEach(img => img.classList.remove("show"));
    document.querySelector(`.img-${index}`).classList.add("show");

    const textSlider = document.querySelector(".text_group");
    textSlider.style.transform = `translateY(${-(index - 1) * 2.2}rem)`;

    bullets.forEach(bull => bull.classList.remove("aktuelles_bild"));
    bullets[index - 1].classList.add("aktuelles_bild");
  }

  function startAutoSlide() {
    intervalId = setInterval(changeSlide, 7000);
  }

  function stopAutoSlide() {
    clearInterval(intervalId);
  }

  bullets.forEach((bullet, index) => {
    bullet.addEventListener("click", function() {
      stopAutoSlide();
      updateSlide(index + 1);
      startAutoSlide();
    });
  });
  startAutoSlide();
}


// if result exists on index page, page will be redirected
if (window.location.pathname.includes('/upload')) {
  window.location.hash = '#result';
} else {
  window.location.hash = '';
}


// hide error message after 7 seconds
setTimeout(function() {
  var errorMessage = document.getElementById('error_message');
  if (errorMessage) {
      errorMessage.style.display = 'none';
  }
}, 7000);