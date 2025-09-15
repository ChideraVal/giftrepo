from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.db.models import BooleanField, DurationField, ExpressionWrapper, Q, F
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from datetime import timedelta
from django.utils import timezone
import random
import uuid
from django.conf import settings
from dotenv import load_dotenv
import os
import requests
from django.core.mail import EmailMultiAlternatives, send_mail, get_connection
from django.template.loader import render_to_string
from .mails import (
    send_payment_verification_email,
    send_coin_payment_email,
    send_email_verification_email,
    send_email_verified_email,
    send_change_code_email,
    send_email_changed_email
)

load_dotenv()
secret_key = os.getenv('SECRET_KEY')
        
def not_found(request, exception):
    return render(request, '404.html')

def server_error(request):
    return render(request, '500.html')

def sign_in(request):
    path = request.get_full_path()
    next_url = path.replace('/signin/?next=', '')
    if request.method == 'POST':
        form = CustomAuthForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_verified:
                login(request, user)
                if next_url == '/signin/' or next_url == '/signup/':
                    return redirect('all_gifts')
                return redirect(next_url)    
            else:
                return redirect(f'/verifyemail/{user.id}/?next={next_url}')
        else:
            print(form.errors)
            return render(request, 'signin.html', {'form': form})
    form = CustomAuthForm(request)
    return render(request, 'signin.html', {'form': form})

def sign_up(request):
    path = request.get_full_path()
    next_url = path.replace('/signup/?next=', '')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.profile_pic = random.choice(ProfilePicture.objects.all())

            # generate user unique verify code
            verify_code = str(uuid.uuid4())
            while True:
                print('VERIFY CODE: ', verify_code)
                if User.objects.filter(verify_code=verify_code).exists():
                    verify_code = str(uuid.uuid4())
                else:
                    break
            user.verify_code = str(verify_code)
            user.save()

            # verify email logic
            if user.is_verified:
                login(request, user)
                print('NEXT URL POST: ', next_url)
                if next_url == '/signin/' or next_url == '/signup/':
                    return redirect('all_gifts')
                return redirect(next_url)
            else:
                email_value = send_email_verification_email(request, user.id)
                print(email_value)
                return redirect(f'/verifyemail/{user.id}/?next={next_url}')
        else:
            print(form.errors)
            return render(request, 'signup.html', {'form': form})
    print('NEXT URL GET: ', next_url)
    form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def verify_email(request, user_id):
    path = request.get_full_path()
    user = get_object_or_404(User, id=user_id)

    next_url = path.replace(f'/verifyemail/{user.id}/?next=', '')
    if request.method == 'POST':
        if user.is_verified:
            login(request, user)
            print('NEXT URL POST: ', next_url)
            if next_url == '/signin/' or next_url == '/signup/':
                return redirect('all_gifts')
            return redirect(next_url)
        else:
            return render(request, 'verifyemail.html', {'user': user, 'next_url': next_url})
    return render(request, 'verifyemail.html', {'user': user, 'next_url': next_url})

def verify_user(request, verify_code):
    user = get_object_or_404(User, verify_code=verify_code)
    user.is_verified = True
    user.verify_code = None
    user.save()
    email_value = send_email_verified_email(request, user.id)
    print(email_value)
    return render(request, 'verifyemail.html', {'user': user})

def change_email(request, change_email_code):
    user = get_object_or_404(User, change_email_code=change_email_code)
    former_email = user.email
    user.email = user.new_email
    user.new_email = None
    user.change_email_code = None
    user.save()
    email_value = send_email_changed_email(request, user.id)
    print(email_value)
    return render(request, 'emailchanged.html', {'user': user, 'fm': former_email})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(instance=request.user, data=request.POST)
        old_email = request.user.email
        if form.is_valid():
            user = form.save(commit=False)
            user.email = old_email
            user.new_email = form.cleaned_data['email']

            # generate user unique change email code
            change_email_code = str(uuid.uuid4())
            while True:
                print('VERIFY CODE: ', change_email_code)
                if User.objects.filter(change_email_code=change_email_code).exists():
                    change_email_code = str(uuid.uuid4())
                else:
                    break
            user.change_email_code = str(change_email_code)
            user.save()

            email_value = send_change_code_email(request, user.id)
            print(email_value)
            return redirect('profile')
        else:
            print(form.errors)
            return render(request, 'edit_profile.html', {'form': form})
    form = CustomUserChangeForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def change_profile_picture(request):
    profile_pictures = ProfilePicture.objects.all()
    return render(request, "change_profile_picture.html", {'profile_pictures': profile_pictures})

@login_required
def use_profile_picture(request, profile_picture_id):
    profile_picture = get_object_or_404(ProfilePicture, id=profile_picture_id)

    user = request.user
    user.profile_pic = profile_picture
    user.save()

    return redirect('profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
        else:
            print(form.errors)
            return render(request, 'change_password.html', {'form': form})
    form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def deactivate_account(request):
    if request.user.is_pending_deletion():
        return redirect('profile')
    if request.method == 'POST':
        user = request.user
        user.deactivated_at = timezone.now()
        user.save()
        return redirect('profile')
    return render(request, 'verifydelete.html')

@login_required
def cancel_account_deletion(request):
    user = request.user
    user.deactivated_at = None
    user.save()
    return redirect('profile')

@login_required
def sign_out(request):
    logout(request)
    return redirect('signin')

@login_required
def send_gift(request):
    gifts = Gift.objects.all()
    return render(request, "send_gifts.html", {'gifts': gifts})

@login_required
def buy_gift(request, gift_id):
    gift = get_object_or_404(Gift, id=gift_id)
    if request.method == "POST":
        quantity = int(request.POST['quantity'])
        total_cost = int(gift.cost * quantity)
        if request.user.coins < total_cost:
            rem_amount = total_cost - request.user.coins
            return render(request, "need_coins.html", {'gift': gift, 'rem_amount': rem_amount, 'quantity': quantity, 'total_cost': total_cost, 'message': 'send this gift'})
        else:
            form = GiftForm(request.POST)
            if form.is_valid():
                user = request.user
                updated_coins = user.coins - total_cost
                user.coins = updated_coins
                user.save()

                gift_transaction = form.save(commit=False)

                if not gift_transaction.is_fastest_finger:
                    recipients = User.objects.exclude(id=request.user.id)
                    recipient = random.choice(recipients) if recipients.exists() else None
                    gift_transaction.recipient = recipient
                
                expire_date = gift_transaction.created_at + timedelta(hours=gift_transaction.expire_rate)
                drop_date = gift_transaction.created_at + timedelta(hours=gift_transaction.drop_rate)

                gift_transaction.gifter = request.user
                gift_transaction.gift = gift

                gift_transaction.expire_date = expire_date
                gift_transaction.drop_date = drop_date

                gift_transaction.save()
                return render(request, 'gift_success.html', {'gift_transaction': gift_transaction})
    else:
        form = GiftForm()
    return render(request, "buy_gift.html", {'gift': gift, 'form': form})

def check_transaction_status(request, transaction_id):
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    headers = {
        "Authorization": f"Bearer {secret_key}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    return None

@login_required
def activate_purchase(request, transaction_id):
    user = request.user
    transaction_id = str(transaction_id)
    transaction_id_exists_for_coin_purchase = CoinPurchase.objects.filter(transaction_id=transaction_id).exists()
    if transaction_id_exists_for_coin_purchase:
        return redirect('buy_coins')
    if not transaction_id:
        return render(request, 'error.html', {'title': 'Error', 'message': 'Transaction ID missing.'})
    transaction_data = check_transaction_status(request, transaction_id)
    if transaction_data:
        amount = transaction_data['data']['amount']
        coin_amount_mapping = {
            '500': 50,
            '1000': 100,
            '2500': 250,
            '5000': 500,
            '10000': 1000,
            '25000': 2500,

        }
        coins_bought = coin_amount_mapping.get(str(amount), 0)
        if str(transaction_data['status']).lower() == 'success' and str(transaction_data['data']['status']).lower() == 'successful':

            updated_coins = user.coins + coins_bought
            user.coins = updated_coins
            user.save()

            coin_purchase = CoinPurchase.objects.create(
                transaction_id=transaction_id,
                user=user,
                amount=amount,
                coins=coins_bought
            )

            email_value = send_payment_verification_email(request, coin_purchase.id)
            print(email_value)
            return render(request, 'paymentsuccess.html', {'amount': amount, 'coins': coins_bought})
        elif str(transaction_data['data']['status']).lower() == 'failed':
            return render(request, 'paymentfailed.html', {'amount': amount, 'coins': coins_bought})
        else:
            return render(request, 'paymentprocessing.html', {'amount': amount, 'coins': coins_bought})
    return render(request, 'error.html', {'title': 'Error', 'message': 'No transaction data.'})

@login_required
def gift_detail(request, gift_id):
    gift = get_object_or_404(Gift, id=gift_id)
    return render(request, "gifting/gift_detail.html", {"gift": gift})

@login_required
def reveal_gift_early(request, gift_transaction_id):
    gift_transaction = get_object_or_404(GiftTransaction, id=gift_transaction_id)
    if gift_transaction.is_due_for_expire():
        return render(request, 'error.html', {'title': 'Error', 'message': f'This gift has expired and is unavailable.'})
    if gift_transaction.cost > 0 and not gift_transaction.is_fastest_finger and not gift_transaction.is_due_for_drop() and request.user not in gift_transaction.paid_users.all():
        if gift_transaction.gifter == request.user:
            return render(request, 'error.html', {'title': 'Error', 'message': f'You cannot pay coins to view your own gift early.'})
        total_cost = gift_transaction.cost
        if request.user.coins < total_cost:
            rem_amount = total_cost - request.user.coins
            return render(request, "need_coins.html", {'gift': gift_transaction, 'rem_amount': rem_amount, 'total_cost': total_cost, 'message': 'reveal this gift early'})
        user = request.user
        updated_coins = user.coins - gift_transaction.cost
        user.coins = updated_coins
        user.save()
        gift_transaction.paid_users.add(request.user)
        print('CHARGED!')

        gifter = gift_transaction.gifter
        updated_coins = settings.CREDIT_PERCENT * (gifter.won_coins + gift_transaction.cost)
        gifter.won_coins = updated_coins
        gifter.save()
        print('CREDITED!')
        email_value = send_coin_payment_email(request, user.id, gift_transaction.id, settings.CREDIT_PERCENT * gift_transaction.cost, 'Early Reveal')
        print(email_value)
        
    return redirect('reveal_gift', gift_transaction_id=gift_transaction.id)

@login_required
def reveal_gift(request, gift_transaction_id):
    gift_transaction = get_object_or_404(GiftTransaction, id=gift_transaction_id)
    is_winner = (gift_transaction.recipient == request.user)
    if gift_transaction.is_due_for_expire():
        return render(request, 'error.html', {'title': 'Error', 'message': f'This gift has expired and is unavailable.'})
    if gift_transaction.gifter == request.user:
        return render(request, 'error.html', {'title': 'Error', 'message': f'You cannot reveal your own gift.'})
    if gift_transaction.drop_rate > 0:
        # gift has wait time
        if gift_transaction.is_due_for_drop() or request.user in gift_transaction.paid_users.all():

            # charge player entry fee for FF gift
            if gift_transaction.fee > 0 and gift_transaction.is_fastest_finger and request.user not in gift_transaction.reveals.all():
                if gift_transaction.gifter == request.user:
                    return render(request, 'error.html', {'title': 'Error', 'message': f'You cannot pay coins to claim your own FF gift.'})
                total_fee = gift_transaction.fee
                if request.user.coins < total_fee:
                    rem_amount = total_fee - request.user.coins
                    return render(request, "need_coins.html", {'gift': gift_transaction, 'rem_amount': rem_amount, 'total_cost': total_fee, 'message': 'claim this FF gift'})
                user = request.user
                updated_coins = user.coins - gift_transaction.fee
                user.coins = updated_coins
                user.save()
                # gift_transaction.reveals.add(request.user)
                print('CHARGED FOR FF GIFT!')

                gifter = gift_transaction.gifter
                updated_coins = settings.CREDIT_PERCENT * (gifter.won_coins + gift_transaction.fee)
                gifter.won_coins = updated_coins
                gifter.save()
                print('CREDITED FOR FF GIFT!')
                email_value = send_coin_payment_email(request, user.id, gift_transaction.id, settings.CREDIT_PERCENT * gift_transaction.fee, 'FF Entry Fee')
                print(email_value)
            
            # allow claim based on gift mode
            gift_transaction.reveals.add(request.user)

            if gift_transaction.is_fastest_finger:
                
                if gift_transaction.recipient == None:
                    # user wins, credit coins to user (50% of gift value) only when they claim
                    gift_transaction.recipient = request.user
                    # gift_transaction.claim_time = timezone.now()
                    gift_transaction.claimed_by = request.user
                    gift_transaction.save()

                    # credit winner
                    won_coins_to_credit = settings.WIN_PERCENT * (gift_transaction.gift.cost * gift_transaction.quantity)
                    print("WON COINS TO CREDIT: ", won_coins_to_credit)
                    user = request.user
                    updated_won_coins = user.won_coins + won_coins_to_credit
                    user.won_coins = updated_won_coins
                    user.save()

                # check if already claimed by this user and claims is 4 or less
                if not FastestFingerClaim.objects.filter(gift_transaction=gift_transaction, user=request.user).exists() and not FastestFingerClaim.objects.filter(gift_transaction=gift_transaction).count() >= 5:
                    # create ff claim record
                    ff_claim = FastestFingerClaim.objects.create(
                        gift_transaction=gift_transaction,
                        user=request.user
                    )

                    claim_speed = ff_claim.claim_speed()
                    print(f"CLAIM SPEED: {claim_speed}")

                    ff_claim.reaction_time_ms = claim_speed
                    ff_claim.save()



                is_winner = (gift_transaction.recipient == request.user)
                context = {
                    "gift_transaction": gift_transaction,
                    "is_winner": is_winner,
                    "already_claimed": gift_transaction.is_claimed(),
                }
                return render(request, "ff_reveal.html", context)
            else:
                # credit winner only once
                if is_winner and not gift_transaction.is_claimed():
                    won_coins_to_credit = settings.WIN_PERCENT * (gift_transaction.gift.cost * gift_transaction.quantity)
                    print("WON COINS TO CREDIT: ", won_coins_to_credit)
                    user = request.user
                    updated_won_coins = user.won_coins + won_coins_to_credit
                    user.won_coins = updated_won_coins
                    user.save()

                    gift_transaction.claimed_by = request.user
                    gift_transaction.save()

                context = {
                    "gift_transaction": gift_transaction,
                    "is_winner": is_winner,
                    "already_claimed": gift_transaction.is_claimed(),
                }
                return render(request, "reveal.html", context)
        else:
            # block claim
            context = {
                "gift_transaction": gift_transaction,
                # "is_winner": is_winner,
                # "already_claimed": gift_transaction.is_claimed(),
            }
            return render(request, "gift_wait.html", context)
    else:
        # gift is normal and doesn't have wait time
        gift_transaction.reveals.add(request.user)

        # credit winner only once
        if is_winner and not gift_transaction.is_claimed():
            won_coins_to_credit = settings.WIN_PERCENT * (gift_transaction.gift.cost * gift_transaction.quantity)
            print("WON COINS TO CREDIT: ", won_coins_to_credit)
            user = request.user
            updated_won_coins = user.won_coins + won_coins_to_credit
            user.won_coins = updated_won_coins
            user.save()

            gift_transaction.claimed_by = request.user
            gift_transaction.save()
        
        context = {
            "gift_transaction": gift_transaction,
            "is_winner": is_winner,
            "already_claimed": gift_transaction.is_claimed(),
        }
        return render(request, "reveal.html", context)


@login_required
def claim_gift(request, gift_id):
    gift = get_object_or_404(Gift, id=gift_id, recipient=request.user)
    if not gift.is_claimed():
        gift.claimed_by = request.user
        gift.save()
    return render(request, "gifting/claim_success.html", {"gift": gift})

@login_required
def profile(request):
    won = GiftTransaction.objects.filter(reveals=request.user, recipient=request.user).count()
    sent = GiftTransaction.objects.filter(gifter=request.user).count()
    lost = GiftTransaction.objects.filter(reveals=request.user).exclude(recipient=request.user).exclude(gifter=request.user).count()
    context = {
        "won": won,
        "sent": sent,
        "lost": lost,
    }
    return render(request, "profile.html", context)

@login_required
def sent_gifts(request):
    sent = GiftTransaction.objects.annotate(
        due_for_expire=ExpressionWrapper(
            Q(expire_date__lt=timezone.now()), output_field=BooleanField()
        ),
        seconds_before_drop=ExpressionWrapper(
            F("drop_date") - timezone.now(), output_field=DurationField()
        ),
        seconds_before_expire=ExpressionWrapper(
            F("expire_date") - timezone.now(), output_field=DurationField()
        )
    ).filter(gifter=request.user).all().order_by('seconds_before_drop', 'seconds_before_expire')
    context = {
        "gift_transactions": sent,
    }
    return render(request, "sent_gifts.html", context)

@login_required
def won_gifts(request):
    won = GiftTransaction.objects.annotate(
        due_for_expire=ExpressionWrapper(
            Q(expire_date__lt=timezone.now()), output_field=BooleanField()
        ),
        seconds_before_drop=ExpressionWrapper(
            F("drop_date") - timezone.now(), output_field=DurationField()
        ),
        seconds_before_expire=ExpressionWrapper(
            F("expire_date") - timezone.now(), output_field=DurationField()
        )
    ).filter(reveals=request.user, recipient=request.user).all().order_by('seconds_before_drop', 'seconds_before_expire')
    context = {
        "gift_transactions": won,
    }
    return render(request, "won_gifts.html", context)

@login_required
def lost_gifts(request):
    lost = GiftTransaction.objects.annotate(
        due_for_expire=ExpressionWrapper(
            Q(expire_date__lt=timezone.now()), output_field=BooleanField()
        ),
        seconds_before_drop=ExpressionWrapper(
            F("drop_date") - timezone.now(), output_field=DurationField()
        ),
        seconds_before_expire=ExpressionWrapper(
            F("expire_date") - timezone.now(), output_field=DurationField()
        )
    ).filter(reveals=request.user).exclude(recipient=request.user).exclude(gifter=request.user).all().order_by('seconds_before_drop', 'seconds_before_expire')
    context = {
        "gift_transactions": lost,
    }
    return render(request, "lost_gifts.html", context)

@login_required
def gift_stats(request, gift_transaction_id):
    gift_transaction = get_object_or_404(GiftTransaction, id=gift_transaction_id)
    return render(request, "gift_stats.html", {'gift_transaction': gift_transaction})


@login_required
def buy_coins(request):
    return render(request, "buy_coins.html")

@login_required
def wallet(request):
    return render(request, "wallet.html")

# @login_required
def all_gifts(request):
    # gift_transactions = GiftTransaction.objects.all().select_related("gifter", "recipient", "claimed_by")
    # gift_transactions = [gt for gt in GiftTransaction.objects.all() if not gt.is_due_for_expire()]

    # show gifts that are not sent by user
    
    # gift_transactions = GiftTransaction.objects.annotate(
    #     due_for_expire=ExpressionWrapper(
    #         Q(expire_date__lt=timezone.now()), output_field=BooleanField()
    #     ),
    #     seconds_before_drop=ExpressionWrapper(
    #         F("drop_date") - timezone.now(), output_field=DurationField()
    #     ),
    #     seconds_before_expire=ExpressionWrapper(
    #         F("expire_date") - timezone.now(), output_field=DurationField()
    #     )
    # ).filter(due_for_expire=False).exclude(reveals=request.user).exclude(gifter=request.user).order_by('seconds_before_drop', 'seconds_before_expire')

    gift_transactions = GiftTransaction.objects.annotate(
        due_for_expire=ExpressionWrapper(
            Q(expire_date__lt=timezone.now()), output_field=BooleanField()
        ),
        seconds_before_drop=ExpressionWrapper(
            F("drop_date") - timezone.now(), output_field=DurationField()
        ),
        seconds_before_expire=ExpressionWrapper(
            F("expire_date") - timezone.now(), output_field=DurationField()
        )
    ).filter(due_for_expire=False).order_by('seconds_before_drop', 'seconds_before_expire')

    if request.user.is_authenticated:
        gift_transactions = GiftTransaction.objects.annotate(
            due_for_expire=ExpressionWrapper(
                Q(expire_date__lt=timezone.now()), output_field=BooleanField()
            ),
            seconds_before_drop=ExpressionWrapper(
                F("drop_date") - timezone.now(), output_field=DurationField()
            ),
            seconds_before_expire=ExpressionWrapper(
                F("expire_date") - timezone.now(), output_field=DurationField()
            )
        ).filter(due_for_expire=False).exclude(reveals=request.user).exclude(gifter=request.user).order_by('seconds_before_drop', 'seconds_before_expire')

    return render(request, "all_gifts.html", {"gift_transactions": gift_transactions})
