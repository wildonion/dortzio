



from django.urls import path
from .views import *

urlpatterns = [
    path('nft/create/', NFT.create),
    path('nft/edit/', NFT.edit),
    path('nft/get/', NFT.get),
    path('nft/all/', NFT.get_all),
    path('nft/user/', NFT.get_user_nft), #Verify User By Wallet Address & Return His/Her NFTs
    path('nft/img/', NFT.get_media),
    path('nft/offer/', NFT.add_offer), #Add Offer To NFT
    path('nft/get/offer/', NFT.get_offer),
    path('nft/offers/', NFT.get_nft_offers), #Get Offers Of A NFT
    path('nft/edit/offer/', NFT.update_offer_status),
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
    path('nft/unlike/', NFT.dislikes),  #Add Like To An NFT
    path('col/create/', CollectionApi.create),
    path('col/edit/', CollectionApi.edit),
    path('col/get/', CollectionApi.get),
    path('col/all/', CollectionApi.get_all),
    path('col/nfts/', CollectionApi.get_collection_nfts), #Get Collection's NFTs
    path('col/mint/', CollectionApi.collection_mint), #Mint Collection
    path('col/load/', CollectionApi.load_collection),
    path('col/creator/verify/', CollectionApi.verify_collection_creator), #Verify Creator Of Collection
    path('col/limit/', CollectionApi.load_price), #From min to max price of nfts of a collection
    path('col/trd/', CollectionApi.traded), #Traded
    path('col/user/', CollectionApi.user_col), #Users collections
    path('col/verify/', CollectionApi.verify_nft_col_activition), #verify if a nft is in a collection and that collection is activated for shop or not
    path('col/activate/', CollectionApi.activate), #verify if a nft is in a collection and that collection is activated for shop or not
    path('col/nft/ver/cur/', CollectionApi.verify_collection_nft_current_owner), #verify current user of a collection's nft 
    path('col/get/mint/', CollectionApi.minted_nfts),
    path('col/like/', CollectionApi.likes),
    path('col/unlike/', CollectionApi.dislikes),
    path('col/sort/cat/', CollectionApi.sort_by_category), #Loads all collections of all categories
    path('col/gen/create/', GenCollectionApi.create),
    path('col/gen/get/', GenCollectionApi.get),
    path('col/gen/all/', GenCollectionApi.get_all),
    path('col/gen/edit/', GenCollectionApi.edit),
    path('col/gen/get/mint/', GenCollectionApi.minted_nfts),         #Get Minted NFTs Of A Generative Collection
    path('col/gen/add/meta/', GenCollectionApi.nft_metadata),        #Add Json File To Generative Collection
    path('col/gen/get/meta/', GenCollectionApi.get_metadata),
    path('col/gen/asgn/meta/', GenCollectionApi.assign_metadata),    #If Reveal time of a generative collection has come assign nfts metadata saved in json file to template nfts made before
    path('col/gen/all/unrev/', GenCollectionApi.all_unrevealed_collection),
    path('col/gen/rev/', GenCollectionApi.reveal),
    path('col/gen/like/', GenCollectionApi.likes),
    path('col/gen/unlike/', GenCollectionApi.dislikes),
    path('col/gen/creator/', GenCollectionApi.get_creator_gen),
    path('search/', SearchApi.search),
    path('load/cat/', SearchApi.load_by_category), #Loads all collections of a category
]