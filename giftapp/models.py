from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

GENDERS = (
    ('male', 'Male'),
    ('female', 'Female')
)

COIN_BASE_PRICE = 10
GRACE_PERIOD_DAYS = 30


class ProfilePicture(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    image = models.ImageField(null=False, blank=False, upload_to='profile_pics')

    def __str__(self):
        return self.name


class User(AbstractUser):
    gender = models.CharField(max_length=6, choices=GENDERS, default=GENDERS[0][0])
    is_verified = models.BooleanField(default=False, help_text="If the user's email address is verified or not.")
    email = models.EmailField(unique=True, blank=False, null=False)
    coins = models.PositiveIntegerField(default=0)
    won_coins = models.PositiveIntegerField(default=0)
    keys = models.PositiveIntegerField(default=0)
    verify_code = models.CharField(max_length=255, null=True, blank=True)
    profile_pic = models.ForeignKey(ProfilePicture, on_delete=models.SET_NULL, related_name='owners', null=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    # Add gender, location, etc. if need

    def total_won_coin_value(self):
        return self.won_coins * COIN_BASE_PRICE
    
    def is_pending_deletion(self):
        return self.deactivated_at is not None

    def days_since_deactivation(self):
        if not self.deactivated_at:
            return None
        return (timezone.now() - self.deactivated_at).days
    
    def days_until_deactivation(self):
        if not self.deactivated_at:
            return 0
        return max(0, GRACE_PERIOD_DAYS - self.days_since_deactivation())

    def is_grace_period_over(self):
        if not self.deactivated_at:
            return False
        return self.days_since_deactivation() >= GRACE_PERIOD_DAYS


class CoinPurchase(models.Model):
    transaction_id = models.CharField(max_length=256)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coin_purchases")
    amount = models.PositiveIntegerField(help_text="Number of coins user purchased.")
    purchased_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.transaction_id


class Gift(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    cost = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to='gift_images')
    gif = models.FileField(null=True, blank=True, upload_to='gift_gifs')

    def __str__(self):
        return self.name

    def get_value(self):
        return int(self.cost * COIN_BASE_PRICE)


class GiftTransaction(models.Model):
    gifter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gifts_sent")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gifts_received", null=True, blank=True)
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.PositiveIntegerField(default=1, help_text="Number of this gift to buy.")
    cost = models.PositiveIntegerField(default=0, help_text="Number of coins paid to reveal the gift early. FF gifts cannot have early reveal cost greater than 0.")
    fee = models.PositiveIntegerField(default=0, help_text="Number of coins paid to claim FF gifts if paid.")
    paid_users = models.ManyToManyField(User, related_name="paid_gifts", blank=True)
    message = models.CharField(max_length=255, blank=True)
    is_visible = models.BooleanField(default=True, help_text="If the actual gift is shown or hidden.")
    is_fastest_finger = models.BooleanField(default=False, help_text="If the gift is won by fastest finger only.")
    # claim_time = models.DateTimeField(null=True, blank=True)
    # expire time set to max of 24 hours
    expire_rate = models.PositiveIntegerField(default=1, help_text="Number of hours before the gift expires (1 - 24). Must be greater than drop rate.")
    # drop time set to max of 23 hours
    drop_rate = models.PositiveIntegerField(default=0, help_text="Number of hours before the gift drops (0 - 23).")
    expire_date = models.DateTimeField(default=timezone.now)
    drop_date = models.DateTimeField(default=timezone.now)
    
    created_at = models.DateTimeField(default=timezone.now)
    reveals = models.ManyToManyField(User, related_name="gift_reveals", blank=True)
    claimed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="gifts_claimed"
    )

    def __str__(self):
        return f"Gift from {self.gifter} to {self.recipient}"

    def is_claimed(self):
        return self.claimed_by is not None

    def seconds_until_expire(self):
        """
        Returns the number of seconds remaining until the gift expires.
        If it's already due, returns 0 or a negative number (if overdue).
        """
        # expire_date = self.created_at + timedelta(hours=self.expire_rate)
        delta = self.expire_date - timezone.now()
        return max(0, int(delta.total_seconds()))

    def is_due_for_expire(self):
        """
        Returns True if it's time to expire the gifttransaction.
        """
        return self.seconds_until_expire() <= 0
    
    def seconds_until_drop(self):
        """
        Returns the number of seconds remaining until the gift drops.
        If it's already due, returns 0 or a negative number (if overdue).
        """
        # drop_date = self.created_at + timedelta(hours=self.drop_rate)
        delta = self.drop_date - timezone.now()
        return max(0, int(delta.total_seconds()))

    def is_due_for_drop(self):
        """
        Returns True if it's time to expire the gifttransaction.
        """
        return self.seconds_until_drop() <= 0
    
    # def claim_speed(self):
    #     """
    #     Returns the number of seconds the winner claimed the FF gift.
    #     """
    #     drop_date = self.created_at + timedelta(hours=self.drop_rate)
    #     delta = self.claim_time - drop_date
    #     return max(0, round(delta.total_seconds(), 1))
    
    def expire_bar_percent(self):
        return int((self.seconds_until_expire() / (self.expire_rate * 60 * 60)) * 100)
    
    def drop_bar_percent(self):
        return int((self.seconds_until_drop() / (self.drop_rate * 60 * 60)) * 100)


class FastestFingerClaim(models.Model):
    gift_transaction = models.ForeignKey(GiftTransaction, related_name="ff_claims", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim_time = models.DateTimeField(default=timezone.now)
    reaction_time_ms = models.FloatField(null=True)

    # class Meta:
        # unique_together = ("gift_transaction", "user")  # one claim per user
        # ordering = ["reaction_time_ms"]     # fastest first

    def __str__(self):
        return f"{self.user.username} claimed {self.gift_transaction.gift.name} ({self.reaction_time_ms} ms)"
    
    def claim_speed(self):
        """
        Returns the number of seconds the winner claimed the FF gift.
        """
        drop_date = self.gift_transaction.created_at + timedelta(hours=self.gift_transaction.drop_rate)
        delta = self.claim_time - drop_date
        return max(0, round(delta.total_seconds(), 1))


