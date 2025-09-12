// Make payment on flutterwave
function makePayment(amount) {
    const refValue = new Date().toLocaleString();

    console.log(nameValue);
    console.log(emailValue);
    console.log(refValue);

    FlutterwaveCheckout({
        public_key: "1dd5f093-53bb-4de9-a910-cd4612be18f0",
        tx_ref: `${refValue}`,
        amount: Number(amount),
        currency: "NGN",
        payment_options: "card, ussd, banktransfer, account, internetbanking, nqr, applepay, googlepay, enaira, opay",
        customer: {
            email: `${emailValue}`,
            // phone_number: Number(phoneValue),
            name: `${nameValue}`,
        },
        customizations: {
            title: "Bixy",
            description: "Pay now to complete your purchase of Bixy coins.",
        },
        callback: function (payment) {
            open(`https://giftrepo.onrender.com/verify/${payment.transaction_id}/`, '_parent')
        },
    });
}
