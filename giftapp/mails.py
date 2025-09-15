from .models import CoinPurchase, User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

# FUNCTIONS TO SEND EMAILS

def send_payment_verification_email(request, coin_purchase_id):
    coin_purchase = CoinPurchase.objects.get(id=coin_purchase_id)
    mail_to_send = EmailMultiAlternatives(
                    'Payment Made Successfully!',
f"""
Hi {coin_purchase.user.username},

your payment of ₦{coin_purchase.amount} was successful.
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