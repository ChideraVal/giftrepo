from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponse
from .models import *
from django.db.models import Count, Max
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from user_agents import parse
import random
import uuid
import secrets
import json
from django.conf import settings

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
    user.save()
    return render(request, 'verifyemail.html', {'user': user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
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

def deactivate_account(request):
    if request.user.is_pending_deletion():
        return redirect('profile')
    if request.method == 'POST':
        user = request.user
        user.deactivated_at = timezone.now()
        user.save()
        return redirect('profile')
    return render(request, 'verifydelete.html')

def cancel_account_deletion(request):
    user = request.user
    user.deactivated_at = None
    user.save()
    return redirect('profile')

def sign_out(request):
    logout(request)
    return redirect('/signin/')

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
            return render(request, "need_coins.html", {'gift': gift, 'rem_amount': rem_amount, 'quantity': quantity, 'total_cost': total_cost, 'message': 'buy and send this gift'})
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
                    won_coins_to_credit = settings.COIN_PERCENT * (gift_transaction.gift.cost * gift_transaction.quantity)
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
                    won_coins_to_credit = settings.COIN_PERCENT * (gift_transaction.gift.cost * gift_transaction.quantity)
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
            won_coins_to_credit = settings.COIN_PERCENT * (gift_transaction.gift.cost * gift_transaction.quantity)
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
    sent = GiftTransaction.objects.filter(gifter=request.user).all()
    context = {
        "gift_transactions": sent,
    }
    return render(request, "sent_gifts.html", context)

@login_required
def won_gifts(request):
    won = GiftTransaction.objects.filter(reveals=request.user, recipient=request.user).all()
    context = {
        "gift_transactions": won,
    }
    return render(request, "won_gifts.html", context)

@login_required
def lost_gifts(request):
    lost = GiftTransaction.objects.filter(reveals=request.user).exclude(recipient=request.user).exclude(gifter=request.user).all()
    context = {
        "gift_transactions": lost,
    }
    return render(request, "lost_gifts.html", context)

@login_required
def gift_stats(request, gift_transaction_id):
    gift_transaction = get_object_or_404(GiftTransaction, id=gift_transaction_id)
    return render(request, "gift_stats.html", {'gift_transaction': gift_transaction})

# @login_required
def all_gifts(request):
    # gift_transactions = GiftTransaction.objects.all().select_related("gifter", "recipient", "claimed_by")
    # gift_transactions = [gt for gt in GiftTransaction.objects.all() if not gt.is_due_for_expire()]

    # show gifts that are not sent by user
    gift_transactions = GiftTransaction.objects.all()
    return render(request, "all_gifts.html", {"gift_transactions": gift_transactions})
