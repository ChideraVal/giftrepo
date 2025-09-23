from .models import CoinPurchase, User, GiftTransaction
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.template.loader import render_to_string

# FUNCTIONS TO SEND EMAILS

def send_payment_verification_email(request, coin_purchase_id):
    coin_purchase = CoinPurchase.objects.get(id=coin_purchase_id)
    mail_to_send = EmailMultiAlternatives(
                    'Payment Successful!',
f"""
Hi {coin_purchase.user.username},

your payment of ₦{coin_purchase.amount} was successful and {coin_purchase.coins} coin{'s' if coin_purchase.coins == 0 or coin_purchase.coins > 1 else ''} has been credited to your Bixy account.
""",
                    str(settings.DEFAULT_FROM_EMAIL),
                    [str(coin_purchase.user.email)],
                    reply_to=['pyjamelnoreply@mail.com']
                )
    html_page = render_to_string('emails/paymentsuccessmail.html', {
        "coin_purchase": coin_purchase
    })
    mail_to_send.attach_alternative(html_page, 'text/html')
    mail_to_send.send(fail_silently=False)
    return None

def send_coin_payment_email(request, buyer_id, gift_transaction_id, coins, payment_type):
    gift_transaction = GiftTransaction.objects.get(id=gift_transaction_id)
    buyer = User.objects.get(id=buyer_id)
    mail_to_send = EmailMultiAlternatives(
                    'Payment Recieved!',
f"""
Hi {gift_transaction.gifter.username},

you have received a payment of {coins} coin{'s' if coins == 0 or coins > 1 else ''} from {buyer.username} for a gift.
""",
                    str(settings.DEFAULT_FROM_EMAIL),
                    [str(gift_transaction.gifter.email)],
                    reply_to=['pyjamelnoreply@mail.com']
                )
    html_page = render_to_string('emails/coinpaymentsuccessmail.html', {
        "buyer": buyer, "gift_transaction": gift_transaction, "coins": coins, "type": payment_type
    })
    mail_to_send.attach_alternative(html_page, 'text/html')
    mail_to_send.send(fail_silently=False)
    return None

def send_email_verification_email(request, user_id):
    user = User.objects.get(id=user_id)
    mail_to_send = EmailMultiAlternatives(
                    'Verify Your Email Address.',
f"""
Hi {user.username},

your account email address ({user.email}) has not been verified.
""",
                    str(settings.DEFAULT_FROM_EMAIL),
                    [str(user.email)],
                    reply_to=['pyjamelnoreply@mail.com']
                )
    html_page = render_to_string('emails/verifyemailmail.html', {
        "user": user
    })
    mail_to_send.attach_alternative(html_page, 'text/html')
    mail_to_send.send(fail_silently=False)
    return None

def send_email_verified_email(request, user_id):
    user = User.objects.get(id=user_id)
    mail_to_send = EmailMultiAlternatives(
                    'Email Address Verification Successful.',
f"""
Hi {user.username},

your account email address ({user.email}) has been verified.
""",
                    str(settings.DEFAULT_FROM_EMAIL),
                    [str(user.email)],
                    reply_to=['pyjamelnoreply@mail.com']
                )
    html_page = render_to_string('emails/verifyemailsuccessmail.html', {
        "user": user
    })
    mail_to_send.attach_alternative(html_page, 'text/html')
    mail_to_send.send(fail_silently=False)
    return None

def send_change_code_email(request, user_id):
    user = User.objects.get(id=user_id)
    mail_to_send = EmailMultiAlternatives(
                    'Verify Your New Email Address.',
f"""
Hi {user.username},

your account new email address ({user.new_email}) has not been verified.
""",
                    str(settings.DEFAULT_FROM_EMAIL),
                    [str(user.new_email)],
                    reply_to=['pyjamelnoreply@mail.com']
                )
    html_page = render_to_string('emails/verifynewemailmail.html', {
        "user": user
    })
    mail_to_send.attach_alternative(html_page, 'text/html')
    mail_to_send.send(fail_silently=False)
    return None


def send_email_changed_email(request, user_id):
    user = User.objects.get(id=user_id)
    mail_to_send = EmailMultiAlternatives(
                    'New Email Address Verification Successful.',
f"""
Hi {user.username},

your account new email address ({user.email}) has been verified.
""",
                    str(settings.DEFAULT_FROM_EMAIL),
                    [str(user.email)],
                    reply_to=['pyjamelnoreply@mail.com']
                )
    html_page = render_to_string('emails/verifynewemailsuccessmail.html', {
        "user": user
    })
    mail_to_send.attach_alternative(html_page, 'text/html')
    mail_to_send.send(fail_silently=False)
    return None

def send_new_gift_email(request, user_id):
    users = User.objects.exclude(id=user_id).filter(is_verified=True).all()
    connection = get_connection()
    connection.open()
    messages = []

    for user in users:
        mail_to_send = EmailMultiAlternatives(
                    'New Gift on Bixy!',
    f"""
    Hi {user.username},

    Someone just sent a gift on Bixy. Login to view and claim it before it expires.
    """,
                        str(settings.DEFAULT_FROM_EMAIL),
                        to=[str(user.email)],
                        reply_to=['pyjamelnoreply@mail.com']
                    )
        html_page = render_to_string('emails/newgiftmail.html', {
            "user": user
        })
        mail_to_send.attach_alternative(html_page, 'text/html')
        # mail_to_send.send(fail_silently=False)
        messages.append(mail_to_send)

    try:
        connection.send_messages(messages)
    finally:
        connection.close()
    return None