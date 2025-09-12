from django.contrib import admin
from .models import Gift, GiftTransaction, User, ProfilePicture, FastestFingerClaim, CoinPurchase


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'coins', 'won_coins', 'keys', 'is_superuser', 'deactivated_at', 'verify_code')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')


@admin.register(CoinPurchase)
class CoinPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user__username', 'amount')
    search_fields = ('user__username',)
    list_filter = ('amount', 'user__username')


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cost")
    search_fields = ("name",)


@admin.register(GiftTransaction)
class GiftTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "gifter", "recipient", "gift__name", "claimed_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("gifter__username", "recipient__username")


@admin.register(FastestFingerClaim)
class FastestFingerClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "gift_transaction__gift__name", "user__username", "claim_time", "reaction_time_ms")
    list_filter = ("gift_transaction",)
    search_fields = ("reaction_time_ms",)


@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

