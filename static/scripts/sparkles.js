const canvas = document.getElementById("sparkleCanvas");
const ctx = canvas.getContext("2d");

// Handle high DPI screens correctly
function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + "px";
    canvas.style.height = window.innerHeight + "px";
    ctx.setTransform(1, 0, 0, 1, 0, 0); // reset transform
    ctx.scale(dpr, dpr); // scale so drawings stay consistent
}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);

let stars = [];

function createStar() {
    return {
        x: Math.random() * window.innerWidth,
        y: window.innerHeight + 10,
        size: Math.random() * 8 + 5,
        speed: Math.random() * 2 + 1,
        opacity: Math.random() * 0.8 + 0.2
    };
}

function drawStar(star) {
    const spikes = 5;
    const outerRadius = star.size;
    const innerRadius = star.size / 2;

    ctx.save();
    ctx.beginPath();
    ctx.translate(star.x, star.y);
    ctx.moveTo(0, 0 - outerRadius);

    for (let i = 0; i < spikes; i++) {
        ctx.rotate(Math.PI / spikes);
        ctx.lineTo(0, 0 - innerRadius);
        ctx.rotate(Math.PI / spikes);
        ctx.lineTo(0, 0 - outerRadius);
    }

    ctx.closePath();
    ctx.fillStyle = `rgba(102, 126, 234, ${star.opacity})`;
    ctx.fill();
    ctx.restore();
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    stars.forEach((star, i) => {
        star.y -= star.speed;
        if (star.y < -10) stars[i] = createStar();
        drawStar(star);
    });
    requestAnimationFrame(animate);
}

for (let i = 0; i < 40; i++) stars.push(createStar());
animate();
