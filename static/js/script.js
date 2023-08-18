let menu    = document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
};

const scrollItem = ScrollReveal({
    distance:   '65px',
    duration:   1800,
    delay:      1000,
    reset:      true
});

scrollItem.reveal('.main-text'      ,{ delay: 200, origin: 'top' });
scrollItem.reveal('.main-img'       ,{ delay: 350, origin: 'top' });
scrollItem.reveal('.icon'           ,{ delay: 400, origin: 'left' });
scrollItem.reveal('.result-link'    ,{ delay: 400, origin: 'right' });

function getImagePreview(event) {
    var file = event.target.files[0];

    if (file && /\.(jpg|png|jpeg)$/i.test(file.name)) {
        var image           = URL.createObjectURL(file);
        let imageElement    = document.querySelector('.main-img img');
        imageElement.src    = image;
    }
};

window.addEventListener("scroll", function () {
    var targetElement   = document.querySelector("header");
    var scrollPosition  = window.scrollY;

    if (scrollPosition > 0) {
        targetElement.style.background      = "linear-gradient(350.59deg, #4d9559 0%, #38703d 28.53%, #284b41 100%)";
        targetElement.style.paddingTop      = "7px";
        targetElement.style.paddingBottom   = "7px";
    } else {
        targetElement.style.background      = "";
        targetElement.style.paddingTop      = "";
        targetElement.style.paddingBottom   = "";
    }
});