// let cost = "{{ gift_transaction.early_claim_fee }}";

// Example: You’d get these values from Django context
// const userCoins = parseInt("{{ request.user.coins }}");

document.getElementById("earlyButton").addEventListener("click", function (e) {
    const giftCost = cost;
    if (userCoins < giftCost) {
        e.preventDefault(); // stop form submit
        const needed = giftCost - userCoins;
        console.log(needed);
        document.getElementById("neededCoins").textContent = needed.toLocaleString();
        document.getElementById("coinModal").style.display = "flex"; // show modal
    }
});

// Close modal when (X) clicked
document.querySelector(".close").onclick = function () {
    document.getElementById("coinModal").style.display = "none";
};

// Optional: close when clicking outside modal-content
// window.onclick = function(event) {
//   if (event.target == document.getElementById("coinModal")) {
//     document.getElementById("coinModal").style.display = "none";
//   }
// };