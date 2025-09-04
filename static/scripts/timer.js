function startCountdown(elementId) {
    const el = document.getElementById(elementId);
    let seconds = parseInt(el.dataset.seconds);
    let prefix = el.dataset.prefix;

    function update() {
        if (seconds < 0) return;

        let d = Math.floor(seconds / (24 * 3600));
        let h = Math.floor((seconds % (24 * 3600)) / 3600);
        let m = Math.floor((seconds % 3600) / 60);
        let s = seconds % 60;

        el.innerText = `${prefix} in ${d}d ${h}h ${m}m ${s}s`;

        seconds--;
        setTimeout(update, 1000);
    }

    update();
}

const timers = document.getElementsByClassName('timer');
for (timer of timers) {
    startCountdown(`${timer.id}`);
}

const bars = document.getElementsByClassName('bar');
for (bar of bars) {
    bar.style.width = `${bar.id}%`;
}        