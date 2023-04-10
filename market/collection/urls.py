



from django.urls import path
from .views import *

urlpatterns = [
    # path('dev/db/delete', DbOps.delete_db),
    path('nft/create/', NFT.create),
    path('nft/delete/', NFT.delete),
    path('nft/edit/', NFT.edit),
    path('nft/edit/activities', NFT.edit_activities),
    path('nft/edit/price', NFT.edit_price),
    path('nft/get/', NFT.get),
    path('nft/all/', NFT.get_all),
    path('nft/user/', NFT.get_user_nft), #Verify User By Wallet Address & Return His/Her NFTs
    path('nft/creator/', NFT.get_creator_nft), 
    path('nft/img/', NFT.get_media),
    path('nft/offer/', NFT.add_offer), #Add Offer To NFT
    path('nft/get/offer/', NFT.get_offer),
    path('nft/owner/offers/made/', NFT.get_owner_offers_made),
    path('nft/owner/offers/received/', NFT.get_owner_offers_received),
    path('nft/offers/', NFT.get_nft_offers), #Get Offers Of A NFT
    path('nft/offer/cancel/', NFT.cancel_offer),
    path('nft/edit/offer/', NFT.update_offer_status),
    path('nft/offer/check/', NFT.check_offer), 
    path('nft/mint/', NFT.nft_mint), #Mint A NFT
    path('nft/mint/check/', NFT.check_mint), #Check Is User Is Minting Right Amount Of NFTs
    path('nft/auc/', NFT.add_auction), #Add Auction To NFT
    path('nft/auc/done/', NFT.get_done_auction), #Get All Done Auctions Of A NFT(History Of Auctions)
    path('nft/auc/active/', NFT.get_active_auction), #Get One Active Auction Of A NFT
    path('nft/auc/check/', NFT.check_auction),  #Check to see if an auction is done or how much time of it is remaining
    path('nft/auc/end/', NFT.end_auction), #Cancel Active Auction Of NFT
    path('nft/auc/del/', NFT.delete_auc),  #Delete Active Auction Of One NFT
    path('nft/auc/active/all/', NFT.all_active_aucs),  #Get All Active Auctions For All NFTs
    path('nft/auc/add/bid/', NFT.add_auc_bid),  #Get All Active Auctions For All NFTs
    path('nft/auc/active/bids/', NFT.get_nft_ac_auc_bids),  #Get All Active Auction's Bids For An NFT
    path('nft/auc/active/bids/dec/', NFT.decline_w8_bids),  #Decline Waiting Bids Of Active Auction In the end Of an Auction(check auction)
    path('nft/auc/active/bids/max/', NFT.ac_auc_w8_bid_max_price),  #Get NFT active auction max price among waiting bids(check auction)
    path('nft/auc/active/bids/acc/', NFT.accept_bid),  #Change Status Of Largest Bid Of Waiting Bid Of Active Auction Of NFT (check auction)
    path('nft/auc/cancel/bid/', NFT.cancel_bid),
    path('nft/auc/active/bids/wait/', NFT.get_nft_ac_auc_wait_bids),  #Get All Active Auction's Bids For An NFT With "Waiting Status"
    path('nft/auc/get/bid/', NFT.get_all_bid),  #Get All Bids For All NFTs
    path('nft/srch/prop/', NFT.search_p),  #Search NFTs By Their Property
    path('nft/like/', NFT.likes),  #Add Like To An NFT
    path('nft/get/user/likes/', NFT.get_user_likes),  #Add Like To An NFT
    path('nft/unlike/', NFT.dislikes),  #Add Like To An NFT
    path('nft/get/all/activities/', NFT.get_nfts_activity), 
    path('nft/get/owner/all/activities/', NFT.get_owner_nfts_activity),  
    path('nft/get/collections/all/activities/', NFT.get_collection_nfts_activity),  
    path('collection/create/', CollectionApi.create),
    path('collection/delete/', CollectionApi.delete),
    path('collection/edit/', CollectionApi.edit),
    path('collection/edit/offer-floor-price', CollectionApi.edit_offer_floor_price),
    path('collection/get/', CollectionApi.get),
    path('collection/all/', CollectionApi.get_all),
    path('collection/trendings', CollectionApi.get_trendings),
    path('collection/nfts/', CollectionApi.get_collection_nfts), #Get Collection's NFTs
    path('collection/mint/', CollectionApi.collection_mint), #Mint Collection
    path('collection/load/', CollectionApi.load_collection),
    path('collection/creator/verify/', CollectionApi.verify_collection_creator), #Verify Creator Of Collection
    path('collection/limit/', CollectionApi.load_price), #From min to max price of nfts of a collection
    path('collection/trd/', CollectionApi.traded), #Traded
    path('collection/user/', CollectionApi.user_col), #Users collections
    path('collection/verify/', CollectionApi.verify_nft_col_activition), #verify if a nft is in a collection and that collection is activated for shop or not
    path('collection/activate/', CollectionApi.activate), #verify if a nft is in a collection and that collection is activated for shop or not
    path('collection/nft/ver/cur/', CollectionApi.verify_collection_nft_current_owner), #verify current user of a collection's nft 
    path('collection/get/mint/', CollectionApi.minted_nfts),
    path('collection/like/', CollectionApi.likes),
    path('collection/unlike/', CollectionApi.dislikes),
    path('collection/sort/cat/', CollectionApi.sort_by_category), #Loads all collections of all categories
    path('collection/gen/create/', GenCollectionApi.create),
    path('collection/gen/get/', GenCollectionApi.get),
    path('collection/gen/trendings', GenCollectionApi.get_trendings),    
    path('collection/gen/all/', GenCollectionApi.get_all),
    path('collection/gen/edit/', GenCollectionApi.edit),
    path('collection/gen/get/mint/', GenCollectionApi.minted_nfts),         #Get Minted NFTs Of A Generative Collection
    path('collection/gen/add/meta/', GenCollectionApi.nft_metadata),        #Add Json File To Generative Collection
    path('collection/gen/get/meta/', GenCollectionApi.get_metadata),
    path('collection/gen/asgn/meta/', GenCollectionApi.assign_metadata),    #If Reveal time of a generative collection has come assign nfts metadata saved in json file to template nfts made before
    path('collection/gen/all/unrev/', GenCollectionApi.all_unrevealed_collection),
    path('collection/gen/rev/', GenCollectionApi.reveal),
    path('collection/gen/like/', GenCollectionApi.likes),
    path('collection/gen/unlike/', GenCollectionApi.dislikes),
    path('collection/gen/creator/', GenCollectionApi.get_creator_gen),
    path('watchlist/add/', WatchlistApi.add),
    path('watchlist/get/', WatchlistApi.get),
    path('watchlist/remove/', WatchlistApi.remove),
    path('featured/create/', FeaturedApi.create),
    path('featured/get/all/users', FeaturedApi.get_all_user_featureds),
    path('featured/remove/', FeaturedApi.remove),
    path('basket/register/', BasketApi.register),
    path('basket/add/', BasketApi.add),
    path('basket/get/', BasketApi.get),
    path('basket/remove/', BasketApi.remove),
    path('basket/purchase/', BasketApi.purchase),
    path('basket/add-q/', BasketApi.add_q),
    path('basket/remove-q/', BasketApi.remove_q),
    path('basket/remove-all/', BasketApi.remove_all),
    path('search/', SearchApi.search),
    path('load/cat/', SearchApi.load_by_category), #Loads all collections of a category
    path('notif/get/latest/', NotifApi.get_latest_notif), 
    path('notif/register/', NotifApi.register_notif), 
    path('notif/seen/', NotifApi.seen), 
    path('notif/edit/', NotifApi.edit_notif), 
]