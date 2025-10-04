const numberInput = document.getElementById('id_quantity');
const button = document.getElementById('button');

console.log(cost);


button.textContent = `Send For ${(numberInput.value * cost).toLocaleString()}`;


numberInput.addEventListener('input', () => {
    if (numberInput.value && numberInput.value > 0) {
    button.textContent = `Send For ${(numberInput.value * cost).toLocaleString()}`;
    } else {
    button.textContent = `Send For 0`;
    }
})

// Ensure sufficient coins
// const userCoins = parseInt("{{ request.user.coins }}");  

document.getElementById("buyGiftForm").addEventListener("submit", function(e) {
    const giftCost = numberInput.value * cost;
    if (userCoins < giftCost) {
    e.preventDefault(); // stop form submit
    const needed = giftCost - userCoins;
    console.log(needed);
    document.getElementById("neededCoins").textContent = needed.toLocaleString();
    document.getElementById("coinModal").style.display = "flex"; // show modal
    }
});

// Close modal when (X) clicked
document.querySelector(".close").onclick = function() {
    document.getElementById("coinModal").style.display = "none";
};

// Optional: close when clicking outside modal-content
// window.onclick = function(event) {
//   if (event.target == document.getElementById("coinModal")) {
//     document.getElementById("coinModal").style.display = "none";
//   }
// };