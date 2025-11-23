const scrollArea = document.getElementById("scrollArea");
const slides = document.querySelectorAll(".slide");
// alert('SWIPING...')
console.log('--------CONTENT OF THE PAGE-------:', document.body)

// --- 2. STATE VARIABLES ---
let currentIndex = 0;
let adLock = false;
let isScrolling = false; // NEW FLAG: Prevents double skipping

// Variables for Touch Dragging
let touchStartY = 0;
let touchStartScrollTop = 0;
let isDragging = false;

function goToSlide(index) {
    // Prevent going out of bounds
    if (index < 0 || index >= slides.length) return;

    currentIndex = index;

    // 1. Set the cooldown flag immediately
    isScrolling = true;

    const slideHeight = scrollArea.clientHeight; // Calculate height dynamically (fix for resize issues)

    scrollArea.scrollTo({
    top: index * slideHeight,
    behavior: "smooth"
    });

    const slide = slides[index];

    if (slide.dataset.ad === "true") {
    lockAd(slide);
    }

    // 2. Remove the cooldown flag after the scroll animation finishes (approx 800ms)
    setTimeout(() => {
    isScrolling = false;
    }, 100);
}

// WHEEL SCROLL
scrollArea.addEventListener("wheel", (e) => {
    e.preventDefault();

    // CHECK BOTH: If Ad is locked OR if we are currently animating a scroll
    if (adLock || isScrolling) return;

    const dir = e.deltaY > 0 ? 1 : -1;
    const next = currentIndex + dir;

    goToSlide(next);
}, { passive: false });


// 3. Keyboard (Arrow Keys & Space)
window.addEventListener("keydown", (e) => {
    // If locked or scrolling, ignore keys
    if (adLock || isScrolling) return;

    if (e.key === "ArrowDown" || e.key === "ArrowRight" || e.key === " ") {
    e.preventDefault(); // Stop default page scroll
    goToSlide(currentIndex + 1);
    } else if (e.key === "ArrowUp" || e.key === "ArrowLeft") {
    e.preventDefault();
    goToSlide(currentIndex - 1);
    }
});

// --- 4. NEW TOUCH LOGIC (Follow Finger) ---

scrollArea.addEventListener("touchstart", (e) => {
    if (adLock || isScrolling) return;
    
    isDragging = true;
    touchStartY = e.touches[0].clientY;
    touchStartScrollTop = scrollArea.scrollTop; // Remember where we started
}, { passive: false });

scrollArea.addEventListener("touchmove", (e) => {
    if (!isDragging || adLock) return;
    e.preventDefault(); // Stop browser native scroll

    const currentY = e.touches[0].clientY;
    const diff = touchStartY - currentY; // How far finger moved

    // Move screen INSTANTLY with finger
    scrollArea.scrollTo({
    top: touchStartScrollTop + diff,
    behavior: "auto" 
    });
}, { passive: false });


scrollArea.addEventListener("touchend", (e) => {
    if (!isDragging) return;
    isDragging = false;

    const currentY = e.changedTouches[0].clientY;
    const diff = touchStartY - currentY;
    const threshold = window.innerHeight * 0.15; // Drag 15% to change slide

    if (diff > threshold) {
    // Dragged Up -> Next
    goToSlide(currentIndex + 1);
    } else if (diff < -threshold) {
    // Dragged Down -> Prev
    goToSlide(currentIndex - 1);
    } else {
    // Not enough -> Snap back
    goToSlide(currentIndex);
    }
});

function lockAd(slide) {
    adLock = true;
    scrollArea.classList.add("locked");

    const barContainer = slide.querySelector(".progress-container");
    const bar = slide.querySelector(".progress-bar");

    barContainer.style.opacity = 1;
    bar.style.width = "0%";

    let progress = 0;
    const duration = 5;
    const interval = 100;
    const step = 100 / (duration * 1000 / interval);

    const timer = setInterval(() => {
    progress += step;
    bar.style.width = progress + "%";

    if (progress >= 100) {
        clearInterval(timer);
        barContainer.style.opacity = 0;
        scrollArea.classList.remove("locked");
        adLock = false;
    }
    }, interval);
}

// Resize & Init
window.addEventListener('resize', () => {
    const slideHeight = scrollArea.clientHeight;
    scrollArea.scrollTo({ top: currentIndex * slideHeight, behavior: "auto" });
});

// Reset scroll on reload
if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
}
window.scrollTo(0, 0);
scrollArea.scrollTo(0, 0);
