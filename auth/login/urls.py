



from django.urls import path
from .views import UserApi

urlpatterns = [
    path('user/', UserApi.index),
    path('user/login/', UserApi.login),
    path('user/edit/', UserApi.edit),
    path('user/edit/avatar/', UserApi.edit_avatar),
    path('user/edit/banner/', UserApi.edit_banner),
    path('user/get/', UserApi.get_user),
    path('user/all/', UserApi.get_all_users),
    path('user/verify/', UserApi.verify_user),
    path('user/search/', UserApi.search_user),
    path('user/offers/made', UserApi.nft_offers_made),
    path('user/offer/cancel', UserApi.cancel_offer),
    path('user/offers/received', UserApi.nft_offers_received),
    path('user/add/offer/', UserApi.add_offer),
    path('user/all/offer/', UserApi.get_user_all_offers),
    path('user/pend/offer/', UserApi.get_user_waiting_offers),
    path('user/done/offer/', UserApi.get_user_done_offers),
    path('user/edit/offer/', UserApi.update_offer_status),
    path('user/get/offer/', UserApi.get_offer),
    path('user/stat/offer/', UserApi.acc_dec_offer),
]