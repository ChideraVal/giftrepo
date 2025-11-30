from django.contrib import admin
from .models import Gift, GiftTransaction, User, ProfilePicture, CoinPurchase


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'coins', 'won_coins', 'keys', 'is_superuser', 'is_verified', 'verify_code')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser')


@admin.register(CoinPurchase)
class CoinPurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'coinpurchase_user_username', 'amount')
    search_fields = ('user__username',)
    list_filter = ('amount', 'user__username', 'coins')

    def coinpurchase_user_username(self, obj):
        return obj.user.username
    
    coinpurchase_user_username.short_description = 'User'


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cost")
    search_fields = ("name",)


@admin.register(GiftTransaction)
class GiftTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "gifter", "recipient", "gifttransaction_gift_name", "claimed_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("gifter__username", "recipient__username")

    def gifttransaction_gift_name(self, obj):
        return obj.gift.name

    def gifttransaction_gifter_username(self, obj):
        return obj.gifter.username
    
    gifttransaction_gift_name.short_description = 'Gift Name'
    gifttransaction_gifter_username.short_description = 'Gifter'



# @admin.register(FastestFingerClaim)
# class FastestFingerClaimAdmin(admin.ModelAdmin):
#     list_display = ("id", "ffclaim_gifttransaction_gift_name", "ffclaim_user_username", "claim_time", "reaction_time_ms")
#     list_filter = ("gift_transaction",)
#     search_fields = ("reaction_time_ms",)

#     def ffclaim_gifttransaction_gift_name(self, obj):
#         return obj.gift_transaction.gift.name

#     def ffclaim_user_username(self, obj):
#         return obj.user.username
    
#     ffclaim_gifttransaction_gift_name.short_description = 'Gift Name'
#     ffclaim_user_username.short_description = 'User'



@admin.register(ProfilePicture)
class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

