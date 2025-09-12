// Make payment on flutterwave
function makePayment(amount) {
    const refValue = new Date().toLocaleString();

    console.log(nameValue);
    console.log(emailValue);
    console.log(refValue);

    FlutterwaveCheckout({
        public_key: "FLWPUBK-4665a5bfdd9fe8535fa8c74f0d845b09-X",
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
