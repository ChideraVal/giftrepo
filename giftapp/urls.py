from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.templatetags.static import static
from django.views.static import serve
from django.conf import settings
import os

urlpatterns = [
    path('signin/', views.sign_in, name='signin'),
    path('signup/', views.sign_up, name='signup'),
    path('verifyemail/<int:user_id>/', views.verify_email, name='verify_email'),
    path('verifyuser/<slug:verify_code>/', views.verify_user, name='verify_user'),
    path('changeemail/<slug:change_email_code>/', views.change_email, name='change_email'),
    path('logout/', views.sign_out, name='logout'),
    path("gifts/send/", views.send_gift, name="send_gift"),
    path("gifts/buy/<int:gift_id>/", views.buy_gift, name="buy_gift"),
    path('verify/<int:transaction_id>/', views.activate_purchase, name='activate_purchase'),
    path("", views.all_gifts, name="all_gifts"),
    path("profile/", views.profile, name="profile"),
    path("gifts/sent/", views.sent_gifts, name="sent_gifts"),
    path("gifts/won/", views.won_gifts, name="won_gifts"),
    path("gifts/lost/", views.lost_gifts, name="lost_gifts"),
    path("gifts/<int:gift_transaction_id>/stats/", views.gift_stats, name="view_gift_stats"),
    path("buycoins/", views.buy_coins, name="buy_coins"),
    path("wallet/", views.wallet, name="wallet"),
    path("editprofile/", views.edit_profile, name="edit_profile"),
    path("changeprofilepicture/", views.change_profile_picture, name="change_profile_picture"),
    path("useprofilepicture/<int:profile_picture_id>/", views.use_profile_picture, name="use_profile_picture"),
    path("changepassword/", views.change_password, name="change_password"),
    path("deleteaccount/", views.deactivate_account, name="delete_account"),
    path("canceldeletion/", views.cancel_account_deletion, name="cancel_deletion"),
    path("gifts/<int:gift_id>/", views.gift_detail, name="gift_detail"), #temp
    path("gifts/<int:gift_transaction_id>/reveal/", views.reveal_gift, name="reveal_gift"),
    path("gifts/<int:gift_transaction_id>/revealearly/", views.reveal_gift_early, name="reveal_early"),
    path("gifts/<int:gift_id>/claim/", views.claim_gift, name="claim_gift"), #temp
    # PWA: Manifest and Service Worker
    path('manifest.json', RedirectView.as_view(
        url=static('manifest.json'),
        permanent=True
    )),
    path('service-worker.js', lambda request: serve(
    request,
    'service-worker.js',
    document_root=os.path.join(settings.BASE_DIR, 'static')
    )),
    # Asset Links for Android (can stay direct too)
    path('.well-known/assetlinks.json', lambda request: serve(
        request,
        'assetlinks.json',
        document_root=os.path.join(settings.BASE_DIR, 'static/.well-known'),
    )),
]
