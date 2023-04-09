import datetime
import json
import os
import random
import subprocess
import time
from mongoengine import *
from collections import defaultdict
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE, HTTP_302_FOUND
import requests
from django.conf import settings
from .models import *






##### ------------------
#####  constants routes
##### ------------------

user_verify=settings.USER_VERIFY
user_search=settings.USER_SEARCH
edit_nft = settings.NFT_EDIT
nft_offers=settings.NFT_OFFERS
nft_active_auction=settings.NFT_ACTIVE_AUCTION
cancel_user_offer=settings.CANCEL_USER_OFFER
all_active_aucs=settings.NFTS_ACTIVE_AUCTION
check_aucs=settings.CHECK_AUCTION
get_nft_ac_auc_w8_bids = settings.GET_NFT_ACTIVE_AUCTION_WAITING_BIDS
ac_auc_w8_bid_max_price = settings.ACTIVE_AUCTION_WAITING_BIDS_MAX_PRICE
ac_auc_acc_bid = settings.ACCEPT_ACTIVE_AUCTION_BID
get_nft_ac_auc_bids = settings.GET_NFT_ACTIVE_AUCTION_BIDS
col_edit=settings.COLLECTION_EDIT
add_user_offer=settings.ADD_USER_OFFER
get_offer_col_ms=settings.GET_OFFER_COL_MS
user_not_offer=settings.USER_NOT_OFFER
nft_disable_offer=settings.NFT_DISABLE_OFFER
update_offer_status=settings.UPDATE_OFFER_STATUS
get_all_gen_col=settings.GET_ALL_GENERATIVE_COLLECTION
all_unrev_gen_col=settings.ALL_UNREVEALED_GENERATIVE_COLLECTION
assign_metadata=settings.ASSIGN_METADATA
get_col_metadata=settings.GET_GENERATIVE_COLLECTION_METADATA
get_gen_minted_nfts = settings.GET_GENERATIVE_COLLECTION_MINTED_NFT
get_minted_nfts = settings.GET_COLLECTION_MINTED_NFT
ac_auc_dec_w8_bid = settings.ACTIVE_AUCTION_DECLINE_BIDS
delete_db_key_env = settings.DELETE_DB_KEY







# class DbOps:
#     @api_view(['POST'])
#     def delete_db(request):
#         response = Response()
#         delete_db_key = request.data['delete_db_key']
#         if delete_db_key and delete_db_key == delete_db_key_env:
#             from mongoengine.connection import _get_db
#             db = _get_db()
#             db.connection.drop_database('dortzio_nft_marketplace')
#             response.data = {"message": "DELETE DATABASE SUCCESSFULLY", "data": []}
#             response.status_code = HTTP_200_OK
#             return response
#         else:
#             response.data = {"message": "ACCESS DENIED", "data": []}
#             response.status_code = HTTP_403_FORBIDDEN
#             return response
            


##### -------------------
#####     NFT APIs
##### -------------------

class NFT:
    @api_view(['POST'])                                      
    def create(request):
        response = Response()
        col_id = request.data['collection_id']
        perpetual_royalties = request.data['perpetual_royalties']
        title = request.data['title']
        current_owner = request.data['current_owner']
        is_freezed = request.data['is_freezed']
        image = request.FILES['image']
        description = request.data['description']
        expires_at = request.data['expires_at']
        extra = request.data['extra']
        stats = request.data['stats']
        levels = request.data['levels']
        price = request.data['price']
        # links = request.data['links']
        reference = request.data['reference']
        copies = request.data['copies']
        media = request.data['media']
        is_freezed = True if int(is_freezed) == 1 else False 
        if not col_id:
            response.data = {"message": "Enter Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Collections.objects(id=col_id).get()
        if not col:
            response.data = {"message": "Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if NFTs.objects(title=title):
            response.data = {'message': "NFT With That Name Already Exists", 'data': title}
            response.status_code = HTTP_403_FORBIDDEN
            return response
        if reference:
            reference = json.loads(reference)
        col_folder = settings.MEDIA_ROOT
        if not os.path.exists(col_folder):
            os.mkdir(col_folder)
        if not current_owner:
            response.data = {'message': "NFT Must Have Owner", 'data': []}
            response.status_code = HTTP_403_FORBIDDEN
            return response
        image_save_path = settings.MEDIA_ROOT + '/' + 'nft_image_' + str(datetime.datetime.now().timestamp()) + str(image.name).replace(" ", "")
        with open(image_save_path, "wb+") as f:
            for chunk in image.chunks():
                f.write(chunk)
        nft = NFTs(price=price, copies=copies,
                            title=title, description=description, media=media, links=request.data["links"] if "links" in request.data else "",
                            is_freezed=bool(is_freezed), nft_image_path=str(image_save_path), 
                            expires_at=expires_at, updated_at=datetime.datetime.now(), 
                            reference=reference, current_owner=current_owner)
        nft.save()
        if perpetual_royalties:
            perpetual_royalties = json.loads(perpetual_royalties)
            p = len(perpetual_royalties)
            if not p==0:
                for i in range(p):
                    pp = Perpetual_royalties(wallet_address=perpetual_royalties[i]['wallet_address'], royalty=perpetual_royalties[i]['royalty'])
                    nft.perpetual_royalties.append(pp)
                nft.save()
        if extra:
            extra = json.loads(extra) # the front end must send us json stringify
            e = len(extra)
            if not e==0:
                for i in range(e):
                    ex = Property(name=extra[i]['name'], value=extra[i]['value'])
                    nft.extra.append(ex)
            nft.save()
        if stats:
            stats = json.loads(stats) # the front end must send us json stringify
            e = len(stats)
            if not e==0:
                for i in range(e):
                    stat = Stats(name=stats[i]['name'], value=stats[i]['value'], count=stats[i]['count'])
                    nft.stats.append(stat)
            nft.save()
        if levels:
            levels = json.loads(levels) # the front end must send us json stringify
            e = len(levels)
            if not e==0:
                for i in range(e):
                    level = Levels(name=levels[i]['name'], value=levels[i]['value'], count=levels[i]['count'])
                    nft.levels.append(level)
            nft.save()
        s_id = str(nft.id)
        col.nft_ids.append(s_id)
        col.updated_at = datetime.datetime.now()
        col.save()
        response.data = {'message': "NFT Created Successfully", 'data': json.loads(nft.to_json())}
        response.status_code = HTTP_201_CREATED
        return response

    @api_view(['POST'])       
    def edit(request):
        response = Response()
        nft_id = request.data['nft_id']
        c_c = request.data['current_owner']          # If NFT is minted creator can't edit it , current owner can/ before minting creator of nft can edit and update NFT
        title = request.data['title']
        is_freezed = request.data['is_freezed']
        description = request.data['description']
        expires_at = request.data['expires_at']
        extra = request.data['extra']
        price = request.data['price']
        # links = request.data['links']
        approved = request.data['approved_account_ids']
        reference = request.data['reference']
        n_c_o = request.data['new_current_owner']
        media = request.data['media']
        copies = request.data['copies']
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft_image_path = nft.nft_image_path       
        if nft.is_freezed == True:
            response.data = {"message": "Can't Edit NFT Because It's Freezed", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        is_freezed = True if int(is_freezed) == 1 else False 
        if "image" in request.FILES:
            image = request.FILES['image']
            col_folder = settings.MEDIA_ROOT
            if not os.path.exists(col_folder):
                os.mkdir(col_folder)
            nft_image_path = settings.MEDIA_ROOT + '/' + 'logo_' + str(datetime.datetime.now().timestamp()) + str(image.name).replace(" ", "")
            with open(nft_image_path, "wb+") as f:
                for chunk in image.chunks():
                    f.write(chunk)
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response        
        if not c_c:
            response.data = {"message": "Enter Current Owner Of NFT", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        
        pipeline = [
            {
                "$match": {
                    "nft_ids": str(nft_id)
                }
            }
        ]
        fetch_col = Collections.objects.aggregate(pipeline)
        d = None
        if fetch_col:
            for col in fetch_col:
                col_creator = col["creator"]
                d = dict(collection_creator=col_creator) 
        if "creator" in d and d["creator"] == c_c:
            response.data = {"message": "Only The Creator Can Edit The NFT", "data": []}
            response.status_code = HTTP_403_FORBIDDEN
            return response
        if not title:
            title = nft.title
        if title:
            if not title == nft.title:
                found_nft = NFTs.objects(title=title)
                if not found_nft:
                    title = title
                else:
                    response.data = {'message': "NFT With That Name Exists", 'data': title}
                    response.status_code = HTTP_403_FORBIDDEN
                    return response
            title = title
        if not expires_at:
            expires_at = nft.expires_at
        if not price:
            price = nft.price
        if n_c_o:
            if n_c_o==nft.current_owner:
                response.data = {'message': "This Owner Is Currently The Owner Of The NFT", 'data': n_c_o}
                response.status_code = HTTP_403_FORBIDDEN
                return response
            payload = dict(wallet_address=n_c_o)
            # r = requests.post(local_user_verify, data=payload)
            r = requests.post(user_verify, data=payload)
            if not r.status_code==200:
                response.data = {"message": "Current Owner Can Not Be Changed/ User Not Verified", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            nft.current_owner = n_c_o
            nft.save()
            o = Owners(owner_wallet_address=n_c_o)
            nft.owners.append(o)
            nft.save()
        if not n_c_o:
            n_c_o = nft.current_owner
        if not media:
            media = nft.media
        if not description:
            description = nft.description
        if not reference:
            reference = json.dumps(nft.reference)
        if reference:
            reference = json.loads(reference)
        if not approved:
            approved = nft.approved_account_ids
        if approved:
            approved = json.loads(approved)
        if "price_history" in request.data:
            price_history = request.data['price_history'] #### use this in postman call
            if price_history != None:
                if not price_history == []:
                    price_history = json.loads(price_history)
                    nft.price_history = []
                    phl = len(price_history)
                    for i in range(phl):
                        # pj = json.loads(price_history[i])
                        ph = Price_history(owner_wallet_address=price_history[i]['owner_wallet_address'], sold_at=price_history[i]['sold_at'], price=price_history[i]['price'])
                        nft.price_history.append(ph)
                    nft.save()
        if "listings" in request.data:
            listings = request.data['listings'] #### use this in postman call
            if listings != None:
                if not listings == []:
                    listings = json.loads(listings)
                    nft.listings = []
                    l = len(listings)
                    for i in range(l):
                        lst = Listings(from_wallet_address=listings[i]['from_wallet_address'], 
                                       expiration=str(datetime.datetime.fromtimestamp(float(listings[i]['expiration']))),
                                        nft_id=str(nft_id),
                                       price=listings[i]['price'])
                        nft.listings.append(lst)
                    nft.save()
        if "asset_activity" in request.data:
            asset_activity = request.data['asset_activity'] #### use this in postman call
            if asset_activity != None:
                if not asset_activity == []:
                    asset_activity = json.loads(asset_activity)
                    nft.asset_activity = []
                    l = len(asset_activity)
                    for i in range(l):
                        lst = Asset_activity(
                            event=asset_activity[i]['event'], 
                            expiration=str(datetime.datetime.fromtimestamp(float(asset_activity[i]['expiration']))),
                            price=asset_activity[i]['price'], 
                            receiver_id=asset_activity[i]['receiver_id'], 
                            from_wallet_address=asset_activity[i]['from_wallet_address'],
                            date=str(datetime.datetime.fromtimestamp(float(asset_activity[i]['date']))),
                            copies=asset_activity[i]['copies']
                            )
                        nft.asset_activity.append(lst)
                    nft.save()
        if "extra" in request.data:
            extra = request.data['extra'] #### use this in postman call
            if extra != None:
                if not extra == []:
                    extra = json.loads(extra)
                    nft.extra = []
                    e = len(extra)
                    for i in range(e):
                        ex = Property(name=extra[i]['name'], value=extra[i]['value'])
                        nft.extra.append(ex)
                    nft.save()
        if "stats" in request.data:
            stats = request.data['stats'] #### use this in postman call
            if stats != None:
                if not stats == []:
                    stats = json.loads(stats)
                    nft.stats = []
                    e = len(stats)
                    for i in range(e):
                        stat = Stats(name=stats[i]['name'], value=stats[i]['value'], count=stats[i]['count'])
                        nft.stats.append(stat)
                    nft.save()
        if "levels" in request.data:
            levels = request.data['levels'] #### use this in postman call
            if levels != None:
                if not levels == []:
                    levels = json.loads(levels)
                    nft.levels = []
                    e = len(levels)
                    for i in range(e):
                        level = Levels(name=levels[i]['name'], value=levels[i]['value'], count=levels[i]['count'])
                        nft.levels.append(level)
                    nft.save()
        check_update = nft.update(__raw__={'$set': {'title': title, 'description': description,
                            'price': price, 'approved_account_ids': approved, 'media':media, 'links': request.data["links"] if "links" in request.data else "",
                            'expires_at': expires_at, 'updated_at': datetime.datetime.now(), 
                            'is_freezed': bool(is_freezed), 'reference': reference, "copies": int(copies),
                            'current_owner':n_c_o, 'nft_image_path': str(nft_image_path)}})
        if not check_update:
            response.data = {"message": "Something Went Wrong", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if check_update:
            updated_nft = NFTs.objects(id=nft_id).first()
            ####################################################
            # fire sell notif
            user_notif = UserNotif(wallet_address=c_c)
            if user_notif:
                notifs = user_notif.item_sold.notifs
                notifs.append(
                    Notif(
                        seen=False,
                        nft_id=nft_id,
                        nft_owner=n_c_o,
                        price=nft.price,
                        fired_at=datetime.datetime.now(),
                        event_name = "item_sold"
                    )
                ) 
                user_notif.save()
            ####################################################
            ####################################################
            # fire edit nft notif
            user_notif = UserNotif(wallet_address=c_c)
            if user_notif:
                notifs = user_notif.owned_item_updates.notifs
                notifs.append(
                    Notif(
                        seen=False,
                        nft_id=updated_nft.id,
                        nft_owner=updated_nft.current_owner,
                        price=updated_nft.price,
                        fired_at=datetime.datetime.now(),
                        event_name = "owned_item_updates"
                    )
                ) 
                user_notif.save()
            ####################################################
            response.data = {'message': "NFT Updated Successfully", 'data': json.loads(updated_nft.to_json())}
            response.status_code = HTTP_200_OK
            return response
        
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])       
    def edit_activities(request):
        response = Response()
        nft_id = request.data['nft_id']
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response        
        if "price_history" in request.data:
            price_history = request.data['price_history'] #### use this in postman call
            if price_history != None:
                if not price_history == []:
                    price_history = json.loads(price_history)
                    nft.price_history = []
                    phl = len(price_history)
                    for i in range(phl):
                        # pj = json.loads(price_history[i])
                        ph = Price_history(owner_wallet_address=price_history[i]['owner_wallet_address'], sold_at=str(datetime.datetime.fromtimestamp(float(price_history[i]['sold_at']), None)), price=price_history[i]['price'])
                        nft.price_history.append(ph)
                    nft.save()
        if "listings" in request.data:
            listings = request.data['listings'] #### use this in postman call
            if listings != None:
                if not listings == []:
                    listings = json.loads(listings)
                    nft.listings = []
                    l = len(listings)
                    for i in range(l):
                        lst = Listings(from_wallet_address=listings[i]['from_wallet_address'], 
                                        expiration=str(datetime.datetime.fromtimestamp(float(listings[i]['expiration']), None)), 
                                        nft_id=str(nft_id),
                                        price=listings[i]['price'])
                        nft.listings.append(lst)
                    nft.save()
        if "asset_activity" in request.data:
            asset_activity = request.data['asset_activity'] #### use this in postman call
            if asset_activity != None:
                if not asset_activity == []:
                    asset_activity = json.loads(asset_activity)
                    nft.asset_activity = []
                    l = len(asset_activity)
                    for i in range(l):
                        lst = Asset_activity(
                            event=asset_activity[i]['event'], 
                            expiration=str(datetime.datetime.fromtimestamp(float(asset_activity[i]['expiration']), None)), 
                            price=asset_activity[i]['price'], 
                            receiver_id=asset_activity[i]['receiver_id'], 
                            from_wallet_address=asset_activity[i]['from_wallet_address'],
                            date=str(datetime.datetime.fromtimestamp(float(asset_activity[i]['date']), None)), 
                            copies=asset_activity[i]['copies']
                            )
                        nft.asset_activity.append(lst)
                    nft.save()
        if "extra" in request.data:
            extra = request.data['extra'] #### use this in postman call
            if extra != None:
                if not extra == []:
                    extra = json.loads(extra)
                    nft.extra = []
                    e = len(extra)
                    for i in range(e):
                        ex = Property(name=extra[i]['name'], value=extra[i]['value'])
                        nft.extra.append(ex)
                    nft.save()
        check_update = nft.update(__raw__={'$set': {'updated_at': datetime.datetime.now()}})
        if not check_update:
            response.data = {"message": "Something Went Wrong", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if check_update:
            updated_nft = NFTs.objects(id=nft_id).first()
            response.data = {'message': "NFT Updated Successfully", 'data': json.loads(updated_nft.to_json())}
            response.status_code = HTTP_200_OK
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
    
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])       
    def edit_price(request):
        response = Response()
        nft_id = request.data['nft_id']
        price = request.data['price']
        owner = request.data['owner']
        found_nft = NFTs.objects(id=nft_id, current_owner=owner).first()
        if not nft_id or not price or not owner:
            response.data = {"message": "Enter Rquired Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response        
        if not found_nft:
            response.data = {"message": "No NFT Found For This Owner", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        check_update = found_nft.update(__raw__={'$set': {'updated_at': datetime.datetime.now(), "price": str(price)}})
        if not check_update:
            response.data = {"message": "Something Went Wrong", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if check_update:
            pipeline = [
                {
                    "$match": {
                        "nft_ids": str(nft_id)
                    }
                }
            ]
            fetch_col = Collections.objects.aggregate(pipeline)
            for col in fetch_col: 
                l = len(col["nft_ids"])
                if not l>0:
                    floor=0.0
                if l>0:
                    nfts_prices = []
                    for i in col["nft_ids"]:
                        nft = NFTs.objects(id=i).first()
                        price = nft.price
                        nfts_prices.append(price)
                    floor = min(nfts_prices)
                    if floor == " ": floor = str(0.0)
                    col["all_floor_price"].append(floor)
                    updated_col = Collections.objects(id=col["_id"]).update(__raw__={'$set': {'updated_at':datetime.datetime.now(), 'floor_price': str(floor), 'all_floor_price': col["all_floor_price"]}})
            updated_nft = NFTs.objects(id=nft_id).first()
            
            ####################################################
            # fire edit price nft notif for offeror 
            for offer in found_nft.offers:
                user_notif = UserNotif.objects(wallet_address=offer.from_wallet_address).first()
                if user_notif:
                    notifs = user_notif.price_change.notifs
                    notifs.append(
                        Notif(
                            seen=False,
                            nft_id=nft_id,
                            nft_owner=found_nft.current_owner,
                            price=found_nft.price,
                            fired_at=datetime.datetime.now(),
                            event_name = "price_change"
                        )
                    )
                    user_notif.save()
            ####################################################
            
            
            response.data = {'message': "NFT Updated Successfully", 'data': json.loads(updated_nft.to_json())}
            response.status_code = HTTP_200_OK
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################    
    

    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])                 
    def get_nfts_activity(request):
        response = Response()
        if "from" in request.data and "to" in request.data:  
            from_off = request.data['from']
            to_off = request.data['to']
            data = []
            nfts = NFTs.objects
            for nft in nfts:
                pipeline = [
                    {
                        "$match": {
                            "nft_ids": str(nft.id)
                        }
                    }
                ]
                fetch_col = Collections.objects.aggregate(pipeline)
                d = None
                if fetch_col:
                    for col in fetch_col:
                        col_title = col["title"]
                        col_id = col["_id"]
                        d = dict(collection_id=str(col_id), col_title=str(col_title))
                for a in nft.asset_activity:
                    # a_json = json.loads(a.to_json())
                    a_info = {
                        "event": a["event"],
                        "expiration": a["expiration"],
                        "price": a["price"],
                        "receiver_id": a["receiver_id"],
                        "from_wallet_address": a["from_wallet_address"],
                        "date": a["date"],
                        "copies": a["copies"],
                        "collection_title": d["col_title"],
                        "collection_id": d["collection_id"],
                        "nft_image": str(nft.nft_image_path),
                        "nft_name": str(nft.title),
                    }
                    data.append(a_info)
            activities_sorted_based_on_time = sorted(data, key=lambda x: x['date'], reverse=True)
            response.data = {'message': "All NFT Activities Fetched Successfully", 'data': activities_sorted_based_on_time[int(from_off):int(to_off)]}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {'message': "Request Data Cant Be Empty", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        
    @api_view(['POST'])                 
    def get_owner_nfts_activity(request):
        response = Response()
        if "from" in request.data and "to" in request.data and "owner" in request.data:  
            from_off = request.data['from']
            to_off = request.data['to']
            owner = request.data['owner']
            data = []
            nfts = NFTs.objects(current_owner=owner)
            if nfts:
                for nft in nfts:
                    pipeline = [
                        {
                            "$match": {
                                "nft_ids": str(nft.id)
                            }
                        }
                    ]
                    fetch_col = Collections.objects.aggregate(pipeline)
                    d = None
                    if fetch_col:
                        for col in fetch_col:
                            col_title = col["title"]
                            col_id = col["_id"]
                            d = dict(collection_id=str(col_id), col_title=str(col_title))
                    for a in nft.asset_activity:
                        # a_json = json.loads(a.to_json())
                        a_info = {
                            "event": a["event"],
                            "expiration": a["expiration"],
                            "price": a["price"],
                            "receiver_id": a["receiver_id"],
                            "from_wallet_address": a["from_wallet_address"],
                            "date": a["date"],
                            "copies": a["copies"],
                            "collection_title": d["col_title"],
                            "collection_id": d["collection_id"],
                            "nft_image": str(nft.nft_image_path),
                            "nft_name": str(nft.title),
                        }
                        data.append(a_info)
                activities_sorted_based_on_time = sorted(data, key=lambda x: x['date'], reverse=True)
                response.data = {'message': "All NFT Owners Activities Fetched Successfully", 'data': activities_sorted_based_on_time[int(from_off):int(to_off)]}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {'message': "No NFT Found For This User", 'data': []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {'message': "Request Data Cant Be Empty", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
    
    @api_view(['POST'])                 
    def get_collection_nfts_activity(request):
        response = Response()
        if "from" in request.data and "to" in request.data and "collection_id" in request.data:  
            from_off = request.data['from']
            to_off = request.data['to']
            col_id = request.data['collection_id']
            data = []
            col = Collections.objects(id=col_id).first()
            if col:
                nfts = [json.loads(NFTs.objects.filter(id=nft_id).to_json()) for nft_id in col.nft_ids]
                if len(nfts) > 0:
                    nfts = nfts[int(from_off):int(to_off)]
                    for nft in nfts:
                        d = dict(collection_id=str(col.id), col_title=str(col.title))
                        for a in nft[0]["asset_activity"]:
                            # a_json = json.loads(a.to_json())
                            a_info = {
                                "event": a["event"],
                                "expiration": a["expiration"],
                                "price": a["price"],
                                "receiver_id": a["receiver_id"],
                                "from_wallet_address": a["from_wallet_address"],
                                "date": a["date"],
                                "copies": a["copies"],
                                "collection_title": d["col_title"],
                                "collection_id": d["collection_id"],
                                "nft_image": str(nft[0]["nft_image_path"]),
                                "nft_name": str(nft[0]["title"]),
                            }
                            data.append(a_info)
                    activities_sorted_based_on_time = sorted(data, key=lambda x: x['date'], reverse=True)
                    response.data = {'message': "All NFT Collection Activities Fetched Successfully", 'data': activities_sorted_based_on_time[int(from_off):int(to_off)]}
                    response.status_code = HTTP_200_OK
                    return response
            else:
                response.data = {'message': "No NFT Found For This Collection", 'data': []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {'message': "Request Data Cant Be Empty", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
        
        
        
        
    @api_view(['POST'])                 
    def get(request):
        response = Response()
        req_nft_id = request.data['nft_id']
        if not req_nft_id:
            response.data = {'message': "Enter NFT ID", 'data': l}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        find_nft = NFTs.objects(id=req_nft_id).first()
        if not find_nft:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        ##############################
        #### Added By: @wildonion ####
        ##############################
        pipeline = [
            {
                "$match": {
                    "nft_ids": str(req_nft_id)
                }
            }
        ]
        fetch_col = Collections.objects.aggregate(pipeline)
        fetch_gen_col = Gencollections.objects.aggregate(pipeline)
        d = None
        if fetch_col:
            for col in fetch_col:
                col_title = col["title"]
                col_id = col["_id"]
                col_creator = col["creator"]
                col_perpetual_royalties = col["perpetual_royalties"]
                col_desc = col["description"]
                col_floor_price = col["floor_price"]
                payload = dict(wallet_address=col["creator"])
                r = requests.post(user_verify, data=payload)
                username = "" 
                if r.status_code==200:
                    username = r.json()['data']['username']
                    if "avatar_path" in r.json()['data']:
                        avatar_path = r.json()['data']['avatar_path']
                    else:
                        avatar_path = ""
                d = dict(collection_id=str(col_id), col_floor_price=col_floor_price, col_desc=col_desc, collection_title=col_title, 
                         perpetual_royalties=col_perpetual_royalties, collection_creator=col_creator, collection_creator_username=username,
                         collection_creator_avatar=avatar_path)
        if fetch_gen_col:
            for col in fetch_col:
                col_title = col["title"]
                col_id = col["_id"]
                col_creator = col["creator"]
                payload = dict(wallet_address=col["creator"])
                col_perpetual_royalties = col["perpetual_royalties"]
                col_desc = col["description"]
                col_floor_price = col["floor_price"]
                r = requests.post(user_verify, data=payload)
                username = "" 
                if r.status_code==200:
                    username = r.json()['data']['username']
                    avatar_path = r.json()['data']['avatar_path']
                d = dict(collection_id=str(col_id), col_floor_price=col_floor_price, col_desc=col_desc, collection_title=col_title, 
                         perpetual_royalties=col_perpetual_royalties, collection_creator=col_creator, collection_creator_username=username,
                         collection_creator_avatar=avatar_path)
        if not d:
            response.data = {"message": "NFT Not Found In Collection", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not find_nft.views:
            find_nft.views = 0
        find_nft.views += 1
        find_nft.save()
        nft = NFTs.objects(id=req_nft_id).first()
        nft_ids = Collections.objects(id=d["collection_id"]).first().nft_ids
        nft_ids_len = len(Collections.objects(id=d["collection_id"]).first().nft_ids)
        properties = defaultdict(int)
        for p in nft.extra:
            key = p.name, p.value
            properties[key] += 1
        updated_nft_properties = [{'name': name, 'value': value, 'rarity': ((qty/nft_ids_len) * 100)} for (name, value), qty in properties.items()]
        updated_extra_list = [Property(name=p['name'], value=p['value'], rarity=p['rarity']) for p in updated_nft_properties]
        e = len(updated_extra_list)
        nft.extra = []
        for i in range(e):
            ex = Property(name=updated_extra_list[i]['name'], value=updated_extra_list[i]['value'], rarity=updated_extra_list[i]['rarity'])
            nft.extra.append(ex)
        nft.save() 
        NFTs.objects(id=nft.id).update(__raw__={'$set': {'updated_at': datetime.datetime.now()}})
        for nft_id in nft_ids:
            nft = NFTs.objects(id=nft_id).first()
            total_volume = 0 
            for history in nft.price_history:
                total_volume+=float(history.price)
        nft = NFTs.objects(id=req_nft_id).first()
        nft_single = json.loads(nft.to_json())
        payload = dict(wallet_address=nft_single["current_owner"])
        r = requests.post(user_verify, data=payload)
        username = "" 
        if r.status_code==200:
            username = r.json()['data']['username']
            if "avatar_path" in r.json()['data']:  
                avatar_path = r.json()['data']['avatar_path']
            else:
                avatar_path = ""
        nft_single["username"] = username
        nft_single["avatar_path"] = avatar_path
        nft_info = {"nft": nft_single, "total_volume": total_volume}
        ##############################
        #### Ended By: @wildonion ####
        ##############################
        # j = json.loads(nft.to_json())
        l = []
        l.append(d)
        l.append(nft_info)
        response.data = {'message': "NFT And Its Collection Fetched Successfully", 'data': l}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['GET']) 
    def get_all(request):
        response = Response()
        from_off = request.GET.get('from', '')
        to_off = request.GET.get('to', '')
        all_nft = NFTs.objects[int(from_off):int(to_off)]
        data = []
        for nft in all_nft:
            nft_json = json.loads(nft.to_json())
            pipeline = [
                {
                    "$match": {
                        "nft_ids": str(nft.id)
                    }
                }
            ]
            fetch_col = list(Collections.objects.aggregate(pipeline))
            if fetch_col:
                for col in fetch_col:
                    payload = dict(wallet_address=col["creator"])
                    r = requests.post(user_verify, data=payload)
                    if r.status_code==200:
                        username = r.json()['data']['username']
                        nft_json["collection_creator_username"] = username
                        nft_json["collection_creator_avatar"] = r.json()['data']['avatar_path'] if "avatar_path" in r.json()['data'] else ""
            data.append(nft_json)                        
        if all_nft:
            response.data = {'message': "All NFT Fetched Successfully", 'data': data}
            response.status_code = HTTP_200_OK
            return response
        response.data = {"message": "No NFT Found", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])                  
    def delete(request):
        response = Response()
        nft_id = request.data['nft_id']
        deleted_nft = NFTs.objects(id=nft_id).delete()
        if deleted_nft:
            col_info = Collections.objects.filter(nft_ids=nft_id)
            nft_ids = col_info.first().nft_ids
            nft_ids.remove(nft_id)
            col_info.save()
            response.data = {'message': "NFT Deleted Successfully", 'data': []}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response


        
        
    @api_view(['POST'])               
    def get_user_nft(request):
        response = Response()
        wallet_address = request.data['wallet_address']
        dataha = {}
        if not wallet_address:
            response.data = {"message": "Enter Wallet Adress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(current_owner=wallet_address):
            response.data = {"message": "No NFTs Found For This Wallet Address", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nfts = NFTs.objects(current_owner=wallet_address)
        l_n = len(nfts)
        res = []
        for i in range(l_n):
            j = json.loads(nfts[i].to_json())
            pipeline = [
                {
                    "$match": {
                        "nft_ids": str(j["_id"]["$oid"])
                    }
                }
            ]
            fetch_col = Collections.objects.aggregate(pipeline)
            if fetch_col:
                for col in fetch_col:
                    payload = dict(wallet_address=col["creator"])
                    r = requests.post(user_verify, data=payload)
                    if not r.status_code==200:
                        response.data = {"message": "User Not Verified", "data": []}
                        response.status_code = HTTP_400_BAD_REQUEST
                        return response
                    if r.status_code == 200:
                        data = r.json()
                        username = data['data']['username']
                        j["collection_creator_username"] = username 
                        j["collection_creator_avatar"] = data['data']['avatar_path'] if "avatar_path" in data['data'] else ""
                res.append(j)
        if not len(res)>0:
            response.data = {"message": "No NFTs Found For This Wallet Address", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if len(res)>0:
            response.data = {"message": "NFTs Of Wallet Address Fetched Successfully", "data": res}
            response.status_code = HTTP_200_OK
            return response 

    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])               
    def get_creator_nft(request):
        response = Response()
        wallet_address = request.data['wallet_address']
        if not wallet_address:
            response.data = {"message": "Enter Wallet Adress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        find_collections = Collections.objects(creator=wallet_address)
        nfts = []
        for col in find_collections:
            for nft_id in col.nft_ids:
                nft = json.loads(NFTs.objects.filter(id=nft_id).to_json())[0]
                payload = dict(wallet_address=wallet_address)
                r = requests.post(user_verify, data=payload)
                if not r.status_code==200:
                    response.data = {"message": "User Not Verified", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
                if r.status_code == 200:
                    data = r.json()
                    username = data['data']['username']
                    nft["collection_creator_username"] = username 
                    nft["collection_creator_avatar"] = data['data']['avatar_path'] if "avatar_path" in data['data'] else ""        
                nfts.append(nft)
        if not len(nfts)>0:
            response.data = {"message": "No NFTs Found For This Wallet Address", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if len(nfts)>0:
            response.data = {"message": "NFTs Of Wallet Address Fetched Successfully", "data": nfts}
            response.status_code = HTTP_200_OK
            return response            
        else:
            response.data = {"message": "No Collections Found For This Wallet Address", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################

    @api_view(['POST'])                   
    def get_media(request):
        response = Response()
        nft_id = request.data['nft_id']
        nft = NFTs.objects(id=nft_id).first()
        if nft:
            media = nft.media
            response.data = {"message": "Media Fetched Successfully", "data": media}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])                
    def add_offer(request):             #only one offer at a time (if wanna add more change 0 to i) ======> Offer Will be added to user profile
        response = Response()
        nft_id = request.data['nft_id']
        from_w_a = request.data['from_wallet_address']
        offer = request.data['offer']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not offer:
            response.data = {"message": "Enter Offer", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft.current_owner:
            response.data = {"message": "NFT Has Not Been Minted Yet", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        l_o = len(nft.offers)
        # offers = nft.offers
        offer = json.loads(offer)
        if l_o>0:
            for i in range(l_o):
                if nft.offers[i]['from_wallet_address']==from_w_a:
                    if nft.offers[i]['to_wallet_address']==nft.current_owner:
                        if nft.offers[i]['status'] == 'waiting':
                            off = json.loads(nft.offers[i].to_json())
                            payload = dict(offer=json.dumps(off), status='canceled')
                            # r = requests.post(local_update_offer_status, data=payload)
                            r = requests.post(update_offer_status, data=payload)
                            if not r.status_code==200:
                                response.data = {"message": "Users' Pervious Offers' Status Could Not Be Updated Successfully", "data": []}
                                response.status_code = HTTP_400_BAD_REQUEST
                                return response
                            nft.offers[i]['status'] = 'canceled'
                            nft.save()
        o = Offers(nft_id=nft_id,
                nft_media=nft.nft_image_path, 
                nft_title=nft.title, 
                from_wallet_address=from_w_a, 
                to_wallet_address=nft.current_owner, 
                price=offer[0]['price'], 
                expiration = str(datetime.datetime.fromtimestamp(float(offer[0]['expiration']), None)),
                date = str(datetime.datetime.fromtimestamp(float(offer[0]['date']), None)),
                is_active = True,
                status='waiting')
        nft.offers.append(o)
        j_o = json.loads(o.to_json())
        s_o = json.dumps(j_o)
        payload = dict(offer=s_o)
        r = requests.post(add_user_offer, data=payload)
        if not r.status_code==200:
            response.data = {"message": "Offer Could Not Be submitted On NFT Owner Profile Successfully", "data":[]}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        nft.save()
        NFTs.objects(id=nft_id).update(__raw__={'$set': {'updated_at':datetime.datetime.now()}})
        response.data = {"message": "Offer Submitted Successfully", "data": json.loads(nft.to_json())}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])       
    def get_nft_offers(request):
        response = Response()
        nft_id = request.data['nft_id']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        offers = NFTs.objects(id=nft_id).values_list('offers')
        if not offers:
            response.data = {"message": "No Offer Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        j_offers = json.loads(offers.to_json())
        response.data = {"message": "Offers Of Requested NFT Fetched Successfully", "data": j_offers[0]['offers']}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def get_offer(request):
        response = Response()
        offer = request.data['offer']
        if not offer:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(offers__nft_id=offer[0]['nft_id']).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(nft.offers)
        if not l>0:
            response.data = {"message": "No Offers Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if l>0:
            offers = nft.offers
            res = []
            for i in range(l):
                if offers[i]['from_wallet_address'] == offer[0]['from_wallet_address']:
                    if offers[i]['price'] == offer[0]['price']:
                        if offers[i]['status'] == 'waiting':
                            j = json.loads(nft.offers[i].to_json())
                            res.append(j)
                if i+1 == l:
                    if not len(res) > 0:
                        response.data = {"message": "Offer Not Found In NFTs' Offer's List ", "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                        return response
            response.data = {"message": "Offer Fetched Successfully", "data": res}
            response.status_code = HTTP_200_OK
            return response
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])
    def get_owner_offers_made(request):
        response = Response()
        owner = request.data['owner']
        if not owner:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nfts = NFTs.objects()
        if not nfts:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        res = []
        for nft in nfts:
            l = len(nft.offers)
            if l>0:
                for i in range(l):
                    j = json.loads(nft.offers[i].to_json())
                    if j["from_wallet_address"] == str(owner):
                        payload = dict(wallet_address=j["from_wallet_address"])
                        r = requests.post(user_verify, data=payload)
                        if not r.status_code==200:
                            response.data = {"message": "User Not Verified", "data": []}
                            response.status_code = HTTP_400_BAD_REQUEST
                            return response
                        if r.status_code == 200:
                            data = r.json()
                            username = data['data']['username']
                            j["offeror_username"] = username 
                            j["offeror_avatar"] = data['data']['avatar_path'] if "avatar_path" in data['data'] else ""
                        res.append(j)
        if len(res) > 0:
            response.data = {"message": "Offers Fetched Successfully", "data": res}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Owner Has No Offers", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])
    def get_owner_offers_received(request):
        response = Response()
        owner = request.data['owner']
        if not owner:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nfts = NFTs.objects(current_owner=str(owner))
        if not nfts:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        res = []
        for nft in nfts:
            l = len(nft.offers)
            if l>0:
                for i in range(l):
                    j = json.loads(nft.offers[i].to_json())
                    if j["to_wallet_address"] == str(owner):
                        payload = dict(wallet_address=j["to_wallet_address"])
                        r = requests.post(user_verify, data=payload)
                        if not r.status_code==200:
                            response.data = {"message": "User Not Verified", "data": []}
                            response.status_code = HTTP_400_BAD_REQUEST
                            return response
                        if r.status_code == 200:
                            data = r.json()
                            username = data['data']['username']
                            j["offeror_avatar"] = username 
                            j["offeror_username"] = data['data']['avatar_path'] if "avatar_path" in data['data'] else ""
                        res.append(j)
        if len(res) > 0:
            response.data = {"message": "Offers Fetched Successfully", "data": res}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Owner Has No Offers", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################

    @api_view(['POST'])
    def update_offer_status(request):
        response = Response()
        offer = request.data['offer']
        status = request.data['status']
        if not offer:
            response.data = {"message": "Enter Offer", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not status:
            response.data = {"message": "Enter Staus", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        offer = json.loads(offer)
        if not NFTs.objects(id=offer['nft_id']):
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=offer['nft_id']).first()
        l_o = len(nft.offers)
        if not l_o > 0:
            response.data = {"message": "NFT Has No Offer", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if l_o > 0:
            # data = nft.offers
            res = []
            for i in range(l_o):
                if nft.offers[i]['from_wallet_address'] == offer['from_wallet_address']:
                    if nft.offers[i]['to_wallet_address'] == offer['to_wallet_address']:
                        if nft.offers[i]['status'] == offer['status']:
                            if nft.offers[i]['expiration'] == offer['expiration']:
                                if nft.offers[i]['date'] == offer['date']:
                                    if nft.offers[i]['price'] == offer['price']:
                                        nft.offers[i]['status'] = status
                                        j = json.loads(nft.offers[i].to_json())
                                        res.append(j)
            if not len(res) > 0:
                response.data = {"message": "No Such Offer Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response  
            if len(res) > 0:          
                response.data = {"message": "Offer Status Updated Successfully", "data": res}
                response.status_code = HTTP_200_OK
                return response

    @api_view(['POST'])                 
    def nft_mint(request):
        response = Response()
        issued_at = request.data['issued_at']
        tx_hash = request.data['tx_hash']
        nft_id = request.data['nft_id']
        # owners = request.data['owners']
        # price_history = request.data['price_history']
        current_owner = request.data['current_owner']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        # if nft.current_owner:
        #     response.data = {"message": "NFT Already Has Been Minted", "data": []}
        #     response.status_code = HTTP_406_NOT_ACCEPTABLE
        #     return response
        # o = len(owners)
        # for i in range(o):
        #     j = json.loads(owners[i])
        #     ow = Owners(owner_wallet_address=j['owner_wallet_address'])
        #     nft.owners.append(ow)
        # nft.save()
        # p = len(price_history)
        # for i in range(p):
        #     pj = json.loads(price_history[i])
        #     ph = Price_history(owner_wallet_address=pj['owner_wallet_address'], sold_at=pj['sold_at'], price=pj['price'])
        #     nft.price_history.append(ph)
        # nft.save()
        updated_nft = NFTs.objects(id=nft_id).update(__raw__={'$set': {'issued_at': issued_at, 'updated_at': datetime.datetime.now(), 'tx_hash':tx_hash, 'current_owner':current_owner}})
        if not updated_nft:
            response.data = {"message": "NFT Could Not Update", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        if not Collections.objects(nft_ids=nft_id):
            col = Gencollections.objects(nft_ids=nft_id).first()
            col.nft_owners_count += 1
            col.save()
        if not Gencollections.objects(nft_ids=nft_id):
            col = Collections.objects(nft_ids=nft_id).first()
            col.nft_owners_count += 1
            col.save()
        nft = NFTs.objects(id=nft_id).first()
        response.data = {"message": "NFT Minted Successfully", "data": json.loads(nft.to_json())}
        response.status_code = HTTP_200_OK
        return response
    
    @api_view(['POST'])
    def check_mint(request):
        response = Response()
        mint_count = request.data['mint_count']
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not mint_count:
            response.data = {"message": "Enter Mint Count", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not col_id:
            response.data = {"message": "Enter Generative Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not Gencollections.objects(id=col_id):
            response.data = {"message": "No Generative Collection Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        col = Gencollections.objects(id=col_id).first()
        owner_nft_count = 0
        for i in col.nft_ids:
            if NFTs.objects(id=i, current_owner=w_a):
                owner_nft_count += 1
        if col.mint_per_wallet[0].limitable == True:
            m_c = col.mint_per_wallet[0].mint_count
            if int(mint_count) > m_c:
                response.data = {"message": "Requested Mint Count Is Larger Than Generative Collections' Mint Count", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not int(mint_count) > m_c:
                if not owner_nft_count >= m_c:
                    if not owner_nft_count + int(mint_count) > m_c:
                        response.data = {"message": "User Can Mint More NFTs Of This Generative Collection", "data": []}
                        response.status_code = HTTP_200_OK
                        return response
                    if owner_nft_count + mint_count > m_c:
                        response.data = {"message": "User Is Trying To Mint More NFTs Than Generative Collections' Mint Count", "data": []}
                        response.status_code = HTTP_400_BAD_REQUEST
                        return response

    @api_view(['POST'])                    
    def add_auction(request):   #Add New Auction On An NFT
        response = Response()
        nft_id = request.data['nft_id']
        auction = request.data['auction']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(nft_id=nft_id)
        # r = requests.post(local_nft_active_auction,data= payload)
        r = requests.post(nft_active_auction,data= payload)
        if r.status_code == 200:
            response.data = {"message": "This NFT Already Has An Active Auction", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        else:
            auction = json.loads(auction)
            l = len(auction)
            for i in range(l):
                auc = Auction(nft_id=nft_id, is_ended=auction[i]['is_ended'], 
                              start_time=str(auction[i]['start_time']),
                              duration=str(auction[i]['duration']),
                              starting_price=auction[i]['starting_price'], reserve_price=auction[i]['reserve_price'], 
                              include_reserve_price=auction[i]['include_reserve_price'])
                nft.auction.append(auc)
            nft.save()
            NFTs.objects(id=nft_id).update(__raw__={'$set': {'updated_at':datetime.datetime.now()}})
            nft = NFTs.objects(id=nft_id).get()
            response.data = {"message": "Auction Submited Successfully", "data": json.loads(nft.to_json())}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])
    def end_auction(request):
        response = Response()
        nft_id = request.data['nft_id']
        w_a = request.data['wallet_address']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter Wallet_address", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft.current_owner == w_a:
            response.data = {"message": "Only The Owner Of NFT Can Cancel The Active Auction Of NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(nft_id=nft_id)
        # r = requests.post(local_nft_active_auction,data= payload)
        r = requests.post(nft_active_auction,data= payload)
        if not r.status_code == 200:
            response.data = {"message": "This NFT Has No Active Auction", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if r.status_code == 200:
            if nft.auction[-1]['is_ended'] == False:
                updated_nft = NFTs.objects(id=nft_id ,auction__is_ended=False).update(set__auction__S__is_ended=True)
                if not updated_nft:
                    response.data = {"message": "Active Auction Of NFT Could Not Be Canceled Successfully", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
            payload = dict(nft_id=nft_id)
            # r = requests.post(local_ac_auc_dec_w8_bid, data=payload)
            r = requests.post(ac_auc_dec_w8_bid, data=payload)
            if not r.status_code==200:
                response.data = {"message": "NFTs' Active Auctions' Waiting Bids Could Not Declined Successfully", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            
            ####################################################
            # fire end auction notif for auction creator 
            user_notif = UserNotif(wallet_address=nft.current_owner)
            if user_notif:
                notifs = user_notif.auction_expiration.notifs
                notifs.append(
                    Notif(
                        seen=False,
                        nft_id=nft_id,
                        nft_owner=nft.current_owner,
                        price=nft.price,
                        fired_at=datetime.datetime.now(),
                        event_name = "auction_expiration"
                    )
                ) 
                user_notif.save()
            ####################################################
            
            response.data = {"message": "Active Auction Of NFT Canceled Successfully", "data": []}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])                                      
    def get_done_auction(request):   #All Past Done Auctions Of A NFT(History Of Auctions)
        response = Response()
        nft_id = request.data['nft_id']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        # aucs = Auction.objects(nft_id=nft_id)
        aucs = NFTs.objects(id=nft_id).values_list('auction')
        if not aucs:
            response.data = {"message": "No Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        j_aucs = json.loads(aucs.to_json())
        l = len(j_aucs[0]['auction'])
        ac_auc = []
        for i in range(l):
            if j_aucs[0]['auction'][i]['is_ended'] == True:
                ac_auc.append(j_aucs[0]['auction'][i])
        response.data = {"message": "All Past Auctions Of Requested NFT Fetched Successfully", "data": ac_auc}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def get_active_auction(request):  #Get One Active Auction Of A NFT
        response = Response()
        nft_id = request.data['nft_id']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        aucs = nft.auction
        l = len(aucs)
        if not l>0:
            response.data = {"message": "No Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not nft.auction[-1]['is_ended'] == False:
            response.data = {"message": "No Active Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if nft.auction[-1]['is_ended'] == False:
            j = json.loads(nft.auction[-1].to_json())
            data = []
            data.append(j)
            response.data = {"message": "The Active Auction Of Requested NFT Fetched Successfully", "data": data}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['GET'])
    def all_active_aucs(request):   #All Active Auctions For All NFTs
        response = Response()
        info = NFTs.objects.values_list('id')
        if not info:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(info)
        res = []
        for i in range(l):
            payload = dict(nft_id=info[i])
            # r = requests.post(local_nft_active_auction, data=payload)
            r = requests.post(nft_active_auction, data=payload)
            if r.status_code==200:
                s = dict(nft_id=str(info[i]), data=r.json()['data'])
                res.append(s)
        response.data = {"message": "All Active Auctions For All NFTs", "data": res}
        response.status_code = HTTP_200_OK
        return response   

    @api_view(['GET'])
    def check_auction(request):
        response = Response()
        # r = requests.get(local_all_active_aucs)
        r = requests.get(all_active_aucs)
        if not r.status_code==200:
            response.data = {"message": "No Active Auction Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        ended_aucs = []
        resp = r.json()['data']
        l = len(resp)
        for i in range(l):
            end = int(float(resp[i]['data'][0]['start_time'])) + int(float(resp[i]['data'][0]['duration'])) #milisecs
            if int(time.time())*1000 >= end:
                ended_aucs.append(resp[i])
            else:
                pass
        l = len(ended_aucs)
        if l==0:
            response.data = {"message": "No Auction Ended", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not l==0:
            for i in range(l):
                nft_id = ended_aucs[i]['nft_id']
                nft = NFTs.objects(id=nft_id).first()
                l_bids = len(nft.auction[-1].bids)
                if l_bids>0:
                    w8_bids = 0
                    for j in range(l_bids):
                        if not nft.auction[-1].bids[j]['status'] == 'waiting':
                            if j+1==l_bids:
                                if not w8_bids>0:
                                    NFTs.objects(id=nft_id, auction__is_ended=False).update(set__auction__S__is_ended=True)
                        if nft.auction[-1].bids[j]['status'] == 'waiting':
                            w8_bids+=1
                    if w8_bids>0:
                        payload = dict(nft_id=nft_id)
                        # r = requests.post(local_ac_auc_w8_bid_max_price, data=payload)
                        r = requests.post(ac_auc_w8_bid_max_price, data=payload)
                        if not r.status_code==200:
                            response.data = {"message": "Max Price Of Active Auction Could Not Be Fetched Successfully", "data": []}
                            response.status_code = HTTP_400_BAD_REQUEST
                            return response
                        NFTs.objects(id=nft_id, auction__is_ended=False).update(set__auction__S__is_ended=True)
                        max_price = r.json()['data']
                        payload = dict(nft_id=nft_id, price=max_price)
                        # r = requests.post(local_ac_auc_acc_bid, data=payload)
                        r = requests.post(ac_auc_acc_bid, data=payload)
                        if not r.status_code==200:
                            response.data = {"message": "NFTs' Active Auctions' Bid Could Not Be Accepted Successfully", "data": []}
                            response.status_code = HTTP_400_BAD_REQUEST
                            return response
                        payload = dict(nft_id=nft_id)
                        # r = requests.post(local_ac_auc_dec_w8_bid, data=payload)
                        r = requests.post(ac_auc_dec_w8_bid, data=payload)
                        if not r.status_code==200:
                            response.data = {"message": "NFTs' Active Auctions' Waiting Bids Could Not Declined Successfully", "data": []}
                            response.status_code = HTTP_400_BAD_REQUEST
                            return response
            response.data = {"message": "These Auctions Have Become To An End", "data": ended_aucs}
            response.status_code = HTTP_200_OK
            return response
    
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['GET'])
    def check_offer(request):
        response = Response()
        pipeline = [
            {
                "$match": {
                    "offers.is_active": True
                }
            }
        ]
        active_offers_for_nft = NFTs.objects.aggregate(pipeline)
        if not active_offers_for_nft:
            response.data = {"message": "No Offer Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        
        updateds = []
        for nft in active_offers_for_nft:
            for offer_index in range(len(nft["offers"])):
                offer_expiration = nft["offers"][offer_index]["expiration"]
                now = datetime.datetime.now()
                if offer_expiration >= now.strftime("%m/%d/%Y %H:%M:%S"):
                    o = Offers(nft_id=nft["offers"][offer_index]["nft_id"],
                                nft_media=nft["offers"][offer_index]["nft_media"], 
                                nft_title=nft["offers"][offer_index]["nft_title"], 
                                from_wallet_address=nft["offers"][offer_index]["from_wallet_address"], 
                                to_wallet_address=nft["offers"][offer_index]["to_wallet_address"], 
                                price=nft["offers"][offer_index]["price"], 
                                expiration = nft["offers"][offer_index]["expiration"],
                                date = nft["offers"][offer_index]["date"],
                                is_active = False,
                                status="canceled")
                    nft["offers"][offer_index] = o
            NFTs.objects(id=nft["_id"]).update_one(set__offers=nft["offers"])
            # check_update = NFTs.objects(id=nft["_id"]).update(__raw__={'$set': {
                # 'offers': json.loads(json.dumps(nft["offers"])),
                # 'updated_at':datetime.datetime.now()
                # }})      
            updateds.append("ok") 
        if len(updateds) >= 1:
            response.data = {"message": "Checked Offer", "data": []}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Can't Check Active Offers", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        
    ##############################
    #### Ended By: @wildonion ####
    ##############################

    @api_view(['POST'])
    def decline_w8_bids(request):
        response = Response()
        nft_id = request.data['nft_id']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        l_bids = len(nft.auction[-1].bids)
        for j in range(l_bids):
            if nft.auction[-1].bids[j]['status'] == 'waiting':
                nft.auction[-1].bids[j]['status'] = 'declined'
                nft.auction[-1].bids[j]['is_auction_ended'] = 'true'
        nft.save()
        response.data = {"message": "NFTs' Active Auctions' Waiting Bids Declined Successfully", "data": []}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def accept_bid(request):
        response = Response()
        nft_id = request.data['nft_id']
        price = request.data['price']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not price:
            response.data = {"message": "Enter Price", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        l_bids = len(nft.auction[-1].bids)
        bids = nft.auction[-1].bids 
        for j in range(l_bids):
            if bids[j]['price'] == price:
                if bids[j]['status'] == 'waiting':
                    nft.auction[-1].bids[j]['status'] = 'accepted'
                    nft.auction[-1].bids[j]['is_auction_ended'] = 'true'
                    payload = dict(nft_id=nft_id, current_owner=nft.current_owner, new_current_owner=bids[j]['from_wallet_address'],title="", description="", expires_at="" , extra="", price="", perpetual_royalties="", reference="", media="", price_history="", listings ="", approved_account_ids="")
                    # r = requests.post(local_edit_nft, data=payload)
                    r = requests.post(edit_nft, data=payload)
                    if not r.status_code==200:
                        response.data = {"message": "NFT Could Not Transfer Successfully", "data": []}
                        response.status_code = HTTP_406_NOT_ACCEPTABLE
                        return response
                    nft.save()
        response.data = {"message": "NFTs' Active Auctions' Bid Accepted Successfully", "data": []}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def ac_auc_w8_bid_max_price(request):
        response = Response()
        nft_id = request.data['nft_id']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        payload = dict(nft_id=nft_id)
        # r = requests.post(local_get_nft_ac_auc_w8_bids, data=payload)
        r = requests.post(get_nft_ac_auc_w8_bids, data=payload)
        if not r.status_code==200:
            response.data = {"message": "NFTs' Active Auctions' Waiting Bids Could Not Be Fetched Successfully", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        data = r.json()['data']
        max_price = data[-1]['price']
        response.data = {"message": "NFTs' Active Auctions' MAX Price Among Waiting Bids Calculated Successfully", "data": max_price}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def add_auc_bid(request):
        response = Response()
        nft_id = request.data['nft_id']
        bid = request.data['auction_bid']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id, auction__is_ended=False).first()
        payload = dict(nft_id=nft_id)
        # r = requests.post(local_nft_active_auction, payload)
        r = requests.post(nft_active_auction, payload)
        if not r.status_code==200:
            response.data = {"message": "No Active Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        ac_auc = r.json()['data']
        ac_auc_end_time = int(float(ac_auc[0]['start_time'])) + int(float(ac_auc[0]['duration']))
        payload = dict(nft_id=nft_id)
        # r = requests.post(local_get_nft_ac_auc_w8_bids, data=payload)
        r = requests.post(get_nft_ac_auc_w8_bids, data=payload)
        l = len(r.json()['data'])
        bid = json.loads(bid)
        if not l>0:
            a = round(float(ac_auc[0]['starting_price']), 4)
            b = round(float(bid[0]['price']), 4)
            if not b >= a:
                response.data = {"message": "Bid Price Should Be Greater Or Equal To The Starting Price", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response    
        if l>0:
            data = r.json()['data']
            a = round(float(data[l-1]['price']), 4)
            b = round(float(bid[0]['price']), 4)
            if not b > a:
                response.data = {"message": "Bid Price Should Be Greater Than Last Bid", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            l_bids = len(nft.auction[-1].bids)
            for j in range(l_bids):
                if nft.auction[-1].bids[j]['from_wallet_address'] == bid[0]['from_wallet_address']:
                    if nft.auction[-1].bids[j]['status'] == 'waiting':
                        nft.auction[-1].bids[j]['status'] = 'canceled'
            nft.save()
        if not 60 + int(datetime.datetime.now().timestamp()) > ac_auc_end_time:    
            nft.auction[-1]['duration'] = str(int(ac_auc[0]['duration'])+300000)
            nft.save()
        nft=NFTs.objects(id=nft_id).first()
        dict_auc_bid = dict(from_wallet_address=bid[0]['from_wallet_address'], price=bid[0]['price'], nft_id=nft_id, is_auction_ended=False, status='waiting')
        nft.auction[-1].bids.append(dict_auc_bid)
        nft.save()
        
        ####################################################
        # fire bid notif
        user_notif = UserNotif(wallet_address=nft.current_owner)
        if user_notif:
            notifs = user_notif.bid_activity.notifs
            notifs.append(
                Notif(
                    seen=False,
                    nft_id=nft_id,
                    nft_owner=nft.current_owner,
                    price=nft.price,
                    fired_at=datetime.datetime.now(),
                    event_name = "bid_activity"
                )
            ) 
            user_notif.save()
        ####################################################
        
        ####################################################
        # fire higher bid notif
        bids = nft.auction[-1].bids
        maxPricedBid = max(bids, key=lambda x:x['price'])
        lowPricedBid = min(bids, key=lambda x:x['price'])
        lowPricedBid_who = None
        for bid in bids:
            if bid["price"] == lowPricedBid:
                lowPricedBid_who = bid["from_wallet_address"]
        user_notif = UserNotif(wallet_address=lowPricedBid_who)
        if user_notif:
            notifs = user_notif.higher_bid.notifs
            notifs.append(
                Notif(
                    seen=False,
                    nft_id=nft_id,
                    nft_owner=nft.current_owner,
                    price=price.nft.price,
                    fired_at=datetime.datetime.now(),
                    event_name = "higher_bid"
                    
                )
            ) 
            user_notif.save()
        ####################################################
            
            
            
        response.data = {"message": "Bids Added Successfully", "data": json.loads(nft.to_json())}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def delete_auc(request):
        response = Response()
        nft_id = request.data['nft_id']
        if not nft_id:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        updated_nft = NFTs.objects(id=nft_id, auction__is_ended=False).update(pull__auction__is_ended=False)
        if not updated_nft:
            response.data = {"message": "Active Auction Could Not Be Deleted Successfully", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        response.data = {"message": "Active Auction Deleted Successfully", "data": []}
        response.status_code = HTTP_200_OK
        return response
        
    @api_view(['POST'])
    def get_nft_ac_auc_bids(request):
        response = Response()
        nft_id = request.data['nft_id']
        payload = dict(nft_id=nft_id)
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        # r = requests.post(local_nft_active_auction, payload)
        r = requests.post(nft_active_auction, payload)
        if not r.status_code==200:
            response.data = {"message": "No Active Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        bids = nft.auction[-1].bids
        if not bids:
            response.data = {"message": "No Bids Found For The Active Auction", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        response.data = {"message": "Bids Of Active Auction Fetched Successfully", "data": bids}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def get_nft_ac_auc_wait_bids(request):
        response = Response()
        nft_id = request.data['nft_id']
        payload = dict(nft_id=nft_id)
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        # r = requests.post(local_nft_active_auction, payload)
        r = requests.post(nft_active_auction, payload)
        if not r.status_code==200:
            response.data = {"message": "No Active Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(nft.auction)
        bids = nft.auction[l-1].bids
        if not bids:
            response.data = {"message": "No Bids Found For The Active Auction", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        b = []
        l = len(bids)
        for i in range(l):
            if bids[i]['status']=='waiting':
                b.append(bids[i])
        if not b:
            response.data = {"message": "No Waiting Bids For The Active Auction Of NFT", "data": []}
            response.status_code = HTTP_200_OK
            return response
        response.data = {"message": "Waiting Bids Of Active Auction Fetched Successfully", "data": b}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['GET'])
    def get_all_bid(request):
        response = Response()
        auc_bids = NFTs.objects.auction.bids
        l = len(auc_bids)
        if not l>0:
            response.data = {"message": "No Bids Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if l>0:
            j_auc_bids = json.loads(auc_bids.to_json())
            response.data = {"message": "All Auction Bids Fetched Successfully", "data": j_auc_bids}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])
    def cancel_bid(request):
        response = Response()
        w_a = request.data['wallet_address']
        nft_id = request.data['nft_id']
        if not w_a:
            response.data = {"message": "Enter Wallet_Address", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        # nft = NFTs.objects(id=nft_id).first()
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(nft_id=nft_id)
        # r = requests.post(local_nft_active_auction, payload)
        r = requests.post(nft_active_auction, payload)
        if not r.status_code==200:
            response.data = {"message": "No Active Auction Found For This NFT", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        l_bids = len(nft.auction[-1].bids)
        if not l_bids>0:
            response.data = {"message": "No Bids Have Been Submitted For Requested NFTs' Active Auction", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if l_bids>0:
            for j in range(l_bids):
                if nft.auction[-1].bids[j]['from_wallet_address'] == w_a:
                    if nft.auction[-1].bids[j]['status'] == 'waiting':
                        nft.auction[-1].bids[j]['status'] = 'canceled'
            nft.save()
            response.data = {"message": "Last Bid Of User Canceled Successfully", "data": []}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])
    def search_p(request):
        response = Response()
        p_name = request.data['property']
        if not p_name:
            response.data = {"message": "Enter NFT Property Name", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nfts = NFTs.objects(extra__name={'$regex' : p_name})
        if not nfts:
            response.data = {"message": "No NFTs Found With The Requested Property", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        j_aucs = json.loads(nfts.to_json())
        l = len(j_aucs)
        if not l>0:
            response.data = {"message": "No NFTs Found With The Requested Property", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        response.data = {"message": "NFTs With The Requested Property Fetched Successfully", "data": j_aucs}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def likes(request):
        response = Response()
        w_a = request.data['wallet_address']
        nft_id = request.data['nft_id']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(wallet_address=w_a)
        # r = requests.post(local_user_verify, data=payload)
        r = requests.post(user_verify, data=payload)
        if not r.status_code==200:
            response.data = {"message": "User Not Verified", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        l = len(nft.likes)
        likes = nft.likes
        if not l>0:
            nft.likes.append(w_a)
            nft.save()
        temp = 0
        if l>0:
            for i in range(l):
                if likes[i]==w_a:
                    response.data = {"message": "This User Has Already Liked This NFT", "data": []}
                    response.status_code = HTTP_403_FORBIDDEN
                    return response
                if not likes[i]==w_a:
                    temp += 1
                    if temp==l:
                        nft.likes.append(w_a)
                        nft.save()
        nft = NFTs.objects(id=nft_id).first()
        response.data = {"message": "NFT Likes Updated Successfully", "data": json.loads(nft.to_json())}
        response.status_code = HTTP_200_OK
        return response

    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])
    def get_user_likes(request):
        response = Response()
        w_a = request.data['wallet_address']
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        payload = dict(wallet_address=w_a)
        # r = requests.post(local_user_verify, data=payload)
        r = requests.post(user_verify, data=payload)
        if not r.status_code==200:
            response.data = {"message": "User Not Verified", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        pipeline = [
            {
                "$match": {
                    "likes": w_a
                }
            }
        ]
        fetch_nfts = NFTs.objects.aggregate(pipeline)
        if fetch_nfts:
            nfts = []
            for nft in fetch_nfts:
                nft["_id"] = str(nft["_id"])
                nfts.append(nft)
            response.data = {"message": "Likes Found", "data": nfts}
            response.status_code = HTTP_200_OK
            return response
        if not fetch_nfts:
            response.data = {"message": "Not Likes Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
    
    @api_view(['POST'])
    def dislikes(request):
        response = Response()
        nft_id = request.data['nft_id']
        w_a = request.data['wallet_address']
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        nft = NFTs.objects(id=nft_id).first()
        if not nft:
            response.data = {"message": "NFT Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(nft.likes)
        likes = nft.likes
        if not l>0:
            response.data = {"message": "NFT Already Has No Likes", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        temp = 0
        if l>0:
            for i in range(l):
                if likes[i]==w_a:
                    nft.likes.remove(likes[i])
                    nft.save()
                    nft = NFTs.objects(id=nft_id).first()
                    response.data = {"message": "NFT Unliked Successfully", "data": json.loads(nft.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                if not likes[i]==w_a:
                    temp += 1
                    if temp==l:
                        response.data = {"message": "This User Had Never Liked This NFT", "data": []}
                        response.status_code = HTTP_406_NOT_ACCEPTABLE
                        return response
                    
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])
    def cancel_offer(request):
        response = Response()
        offer = request.data['offer']
        nft_id = request.data['nft_id']
        if not offer:
            response.data = {"message": "Enter Offer", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not nft_id:
            response.data = {"message": "Enter NFT ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        # nft = NFTs.objects(id=nft_id).first()
        if not NFTs.objects(id=nft_id):
            response.data = {"message": "No NFT Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft = NFTs.objects(id=nft_id).first()
        l_offers = len(nft.offers)
        # offer = json.dumps(offer)
        payload = dict(offer=offer)
        r = requests.post(cancel_user_offer, payload)
        if not l_offers>0:
            response.data = {"message": "No Bids Have Been Submitted For Requested NFTs' Active Auction", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not r.status_code==200:
            response.data = {"message": "No Offer Data Found For User", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        else: # cancel offer if we first cancel the user offer
            offer = json.loads(offer)
            if l_offers>0:
                offers = nft.offers
                for nft_offer in offers:
                    if nft_offer.date == offer[0]["date"] and nft_offer.nft_id == str(nft_id) and nft_offer.is_active == True and nft_offer.from_wallet_address == offer[0]["from_wallet_address"]:
                        if nft_offer.status == 'waiting':
                            nft_offer.status = 'canceled'
                    nft.save()
            response.data = {"message": "Offer Canceled Successfully", "data": json.loads(nft.to_json())}
            response.status_code = HTTP_200_OK
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
                    
                    
##### ------------------------
#####     Collection APIs
##### ------------------------  
class CollectionApi:
    @api_view(['POST'])                
    def create(request):
        response = Response()
        title = request.data['title']
        description = request.data['description']
        creator = request.data['creator']
        category = request.data['category']
        chain = request.data['chain']
        # links = request.data['links']
        logo = request.FILES['logo']
        banner = request.FILES['banner_image']
        extra = request.data['extra']
        perpetual_royalties = request.data['perpetual_royalties']
        if not title:
            response.data = {"message": "Enter Title", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if Collections.objects(title=title):
            response.data = {'message': "NFT Collection With That Name Already Exists", 'data': title}
            response.status_code = HTTP_403_FORBIDDEN
            return response
        if not description:
            response.data = {"message": "Enter Description", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not description:
            response.data = {"message": "Enter Description", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not category:
            response.data = {"message": "Enter Category", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if extra:
            extra = json.loads(extra)
        if perpetual_royalties:
            perpetual_royalties = json.loads(perpetual_royalties)
        if not perpetual_royalties:
            response.data = {"message": "Enter Collection Royalties", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        # logo_extension = os.path.splitext(logo.name)[1]
        col_folder = settings.MEDIA_ROOT
        if not os.path.exists(col_folder):
            os.mkdir(col_folder)
        logo_save_path = settings.MEDIA_ROOT + '/' + 'logo_' + str(datetime.datetime.now().timestamp()) + str(logo.name).replace(" ", "")
        with open(logo_save_path, "wb+") as f:
            for chunk in logo.chunks():
                f.write(chunk)
        # banner_extension = os.path.splitext(banner.name)[1]
        col_folder = settings.MEDIA_ROOT
        if not os.path.exists(col_folder):
            os.mkdir(col_folder)
        banner_save_path = settings.MEDIA_ROOT + '/' + 'banner_' + str(datetime.datetime.now().timestamp()) + str(banner.name).replace(" ", "")
        with open(banner_save_path, "wb+") as f:
            for chunk in banner.chunks():
                f.write(chunk)
        col = Collections(updated_at=datetime.datetime.now(),
                            links=request.data["links"] if "links" in request.data else "",
                            title=title, description=description, creator=creator, 
                            category=category, chain=chain, logo_path=str(logo_save_path), 
                            banner_image_path=str(banner_save_path), extra=extra, 
                            created_at=datetime.datetime.now(), nft_owners_count=0,
                            floor_price=str(0), all_floor_price=[])
        p = len(perpetual_royalties)
        for i in range(p):
            per = Perpetual_royalties(wallet_address=perpetual_royalties[i]['wallet_address'], royalty=perpetual_royalties[i]['royalty'])
            col.perpetual_royalties.append(per)
        col.save()
        if col:
            response.data = {'message': "NFT Collection Created Successfully", 'data': json.loads(col.to_json())}
            response.status_code = HTTP_201_CREATED
            return response

    @api_view(['POST'])             
    def edit(request):
        response = Response()
        col_id = request.data['collection_id']
        creator = request.data['creator']
        title = request.data['title']
        description = request.data['description']
        perpetual_royalties = request.data['perpetual_royalties']
        category = request.data['category']
        # links = request.data['links']
        extra = request.data['extra']
        nfts_prices = []
        if not col_id:
            response.data = {"message": "Enter Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not description:
            response.data = {"message": "Enter Description", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not creator:
            response.data = {"message": "Enter Creator Of Collection", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if perpetual_royalties:
            perpetual_royalties = json.loads(perpetual_royalties)
        if not perpetual_royalties:
            response.data = {"message": "Enter Collection Royalties", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Collections.objects(id=col_id, creator=creator).first()
        if not col:
            response.data = {"message": "Collection With That Creator Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(col.nft_ids)
        if not l>0:
            floor=0
        if l>0:
            for i in col.nft_ids:
                nft = NFTs.objects(id=i).first()
                price = nft.price
                nfts_prices.append(price)
            floor = min(nfts_prices)
        if not col:
            response.data = {"message": "Enter Title", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if title:
            if not title == col.title:
                if not Collections.objects(title=title):
                    title = title
                else:
                    response.data = {"message": "Collection Title Must Be Uinque", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
            else:
                title = col.title
        logo_path = col.logo_path
        banner_image_path = col.banner_image_path
        if "logo" in request.FILES:
            logo = request.FILES['logo']
            # logo_extension = os.path.splitext(logo.name)[1]
            col_folder = settings.MEDIA_ROOT
            if not os.path.exists(col_folder):
                os.mkdir(col_folder)
            logo_path = settings.MEDIA_ROOT + '/' + 'logo_' + str(datetime.datetime.now().timestamp()) + str(logo.name).replace(" ", "")
            with open(logo_path, "wb+") as f:
                for chunk in logo.chunks():
                    f.write(chunk)
        if "banner_image" in request.FILES:
            banner = request.FILES['banner_image']
            # banner_extension = os.path.splitext(banner.name)[1]
            col_folder = settings.MEDIA_ROOT
            if not os.path.exists(col_folder):
                os.mkdir(col_folder)
            banner_image_path = settings.MEDIA_ROOT + '/' + 'banner_' + str(datetime.datetime.now().timestamp()) + str(banner.name).replace(" ", "")
            with open(banner_image_path, "wb+") as f:
                for chunk in banner.chunks():
                    f.write(chunk)
        if not extra:
            extra = col.extra
        else:
            extra = json.loads(extra)
        if not category:
            category = col.category
        p = len(perpetual_royalties)
        perp = []
        for i in range(p):
            per = Perpetual_royalties(wallet_address=perpetual_royalties[i]['wallet_address'], royalty=perpetual_royalties[i]['royalty'])
            perp.append(per)
        col.perpetual_royalties = perp
        col.save()
        check_update = Collections.objects(id=col_id).update(__raw__={'$set': {
                    'title': title, 'category': category, 'links': request.data["links"] if "links" in request.data else "",
                    'description': description, 'extra':extra, 
                    'updated_at':datetime.datetime.now(), 
                    'floor_price': floor, 'logo_path': str(logo_path), 
                    'banner_image_path': str(banner_image_path)}})
        if check_update:
            updated_col = Collections.objects(id=col_id)
            response.data = {'message': "NFT Collection Updated Successfully", 'data': json.loads(updated_col.to_json())}
            response.status_code = HTTP_200_OK
            return response
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    @api_view(['POST'])             
    def edit_offer_floor_price(request):
        response = Response()
        floor_offer_price = request.data['floor_offer_price']
        collection_id = request.data['collection_id']
        nfts_prices = []
        if not floor_offer_price:
            response.data = {"message": "Enter Collection Offer Floor Price", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Collections.objects(id=collection_id).first()
        if not col:
            response.data = {"message": "Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        check_update = Collections.objects(id=collection_id).update(__raw__={'$set': {
                    'floor_offer_price': str(floor_offer_price),
                    'updated_at':datetime.datetime.now()}})
        if check_update:
            updated_col = Collections.objects(id=collection_id)
            response.data = {'message': "Offer Floor Price Updated Successfully", 'data': json.loads(updated_col.to_json())}
            response.status_code = HTTP_200_OK
            return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
    
    
    @api_view(['POST'])          
    def get(request):
        response = Response()
        col_id = request.data['collection_id']
        col = Collections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "NFT Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(col.nft_ids)
        if not l>0:
            floor=0
        if l>0:
            nfts_prices = []
            for i in col.nft_ids:
                nft = NFTs.objects(id=i).first()
                price = nft.price
                nfts_prices.append(price)
            floor = min(nfts_prices)
            if floor == " ": floor = str(0.0) 
        volume = str(col.volume)
        last_volume = str(col.last_volume)
        updated_col = Collections.objects(id=col_id).update(__raw__={'$set': {'updated_at':datetime.datetime.now(), 'floor_price': str(floor), 'volume': volume, 'last_volume': last_volume}})
        if not updated_col:
            response.data = {'message': "Could Not Update Collection Floor Price Before Fetching It", 'data': l}
            response.status_code = HTTP_200_OK
            return response
        if not col.views:
            col.views = 0
        col.views += 1
        col.save()
        col = Collections.objects(id=col_id).first()
        ##############################
        #### Added By: @wildonion ####
        ##############################
        nfts = [NFTs.objects.filter(id=nft_id).first() for nft_id in col.nft_ids] # all collection nfts
        owners = [nft["current_owner"] for nft in nfts]
        unique_owners = set(owners)
        json_nfts = []
        total_price = 0.0
        for nft in nfts:
            nft = json.loads(nft.to_json())
            if nft['price'] != " ":
                total_price += float(nft['price'])
            json_nfts.append(nft)
        payload = dict(wallet_address=col.creator)
        # r = requests.post(local_user_verify, data=payload)
        r = requests.post(user_verify, data=payload)
        if not r.status_code==200:
            response.data = {"message": "User Not Verified", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if r.status_code == 200:
            data = r.json()
            username = data['data']['username']
            avatar_path = data['data']['avatar_path'] if "avatar_path" in data['data'] else "" 
        col = json.loads(col.to_json())
        col['username'] = username
        col['avatar_path'] = avatar_path
        col['nfts'] = json_nfts
        col['total_price'] = str(total_price)
        col["unique_owners"] = unique_owners
        ##############################
        #### Ended By: @wildonion ####
        ##############################
        response.data = {'message': "Collection Fetched Successfully And Floor Price Updated Before Fetching It", 'data': col}
        response.status_code = HTTP_200_OK
        return response


    ##############################
    #### Added By: @wildonion ####
    ##############################
    # NOTE - trending collections is based on the whole price 
    #        number of all successfully completed NFT trades 
    #        for a specific time period. 
    @api_view(['POST'])
    def get_trendings(request):
        response = Response()
        from_ = request.data["from"] # float timestamp
        to = request.data["to"] # float timestamp
        from_col = request.data["from_col"]
        to_col = request.data["to_col"]
        cat = request.data["cat"]
        isodate = None
        collections = None
        if not from_:
            isodate = datetime.datetime.fromtimestamp(float(to), None)
            collections = Collections.objects(created_at__lte=isodate, category=cat) if cat else Collections.objects(created_at__lte=isodate)
        if from_:
            isodate_from = datetime.datetime.fromtimestamp(float(from_), None)
            isodate_to = datetime.datetime.fromtimestamp(float(to), None)
            collections = Collections.objects(created_at__lt=isodate_to, created_at__gte=isodate_from, category=cat) if cat else Collections.objects(created_at__lt=isodate_to, created_at__gte=isodate_from)
        if collections:
            data = []
            for collection in collections:
                last_volume = str(collection.last_volume)
                collection_volume_traded = 0
                nfts = [NFTs.objects.filter(id=nft_id) for nft_id in collection.nft_ids]
                nft_prices = []
                for nft in nfts:
                    nft_prices.append(nft.first().price)
                    total_sucessfull_price = 0
                    for price_history in nft.first().price_history:
                        total_sucessfull_price+=float(price_history.price)
                    collection_volume_traded+=total_sucessfull_price
                if collection_volume_traded != last_volume:
                    last_volume = collection_volume_traded
                floor_price = min(nft_prices) if len(nft_prices) > 0 else 0
                updated_col = Collections.objects(id=collection.id).update(__raw__={'$set': {'updated_at':datetime.datetime.now(), 'floor_price': str(floor_price), 'volume': str(collection_volume_traded), 'last_volume': str(last_volume)}})
                if not updated_col:
                    response.data = {'message': "Could Not Update Collection Floor Price Before Fetching It", 'data': []}
                    response.status_code = HTTP_200_OK
                    return response
            if not from_:
                isodate = datetime.datetime.fromtimestamp(float(to), None)
                collections = Collections.objects(created_at__lte=isodate, category=cat) if cat else Collections.objects(created_at__lte=isodate)
            if from_:
                isodate_from = datetime.datetime.fromtimestamp(float(from_), None)
                isodate_to = datetime.datetime.fromtimestamp(float(to), None)
                collections = Collections.objects(created_at__lt=isodate_to, created_at__gte=isodate_from, category=cat) if cat else Collections.objects(created_at__lt=isodate_to, created_at__gte=isodate_from)
            for collection in collections:
                col_info = Collections.objects.filter(id=collection.id)
                nfts = [NFTs.objects.filter(id=nft_id).first() for nft_id in collection.nft_ids]
                json_nfts = []
                owners = [nft.current_owner for nft in nfts]
                unique_owners = set(owners)
                for nft in nfts:
                    nft = json.loads(nft.to_json())
                    json_nfts.append(nft)
                col = json.loads(col_info.first().to_json())
                payload = dict(wallet_address=col["creator"])
                # r = requests.post(local_user_verify, data=payload)
                r = requests.post(user_verify, data=payload)
                if not r.status_code==200:
                    response.data = {"message": "User Not Verified", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
                if r.status_code == 200:
                    fetched_data = r.json()
                    username = fetched_data['data']['username']
                col['username'] = username
                col['nfts'] = json_nfts
                col['unique_owners'] = unique_owners
                data.append(col)
            response.data = {'message': "All NFT Collection Fetched Successfully", 'data': data[int(from_col):int(to_col)]}
            response.status_code = HTTP_200_OK
            return response
        response.data = {"message": "No NFT Collection Found", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
        return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
    
    
    
    @api_view(['GET']) 
    def get_all(request):
        response = Response()
        from_off = request.GET.get('from', '')
        to_off = request.GET.get('to', '')
        if from_off == '' or to_off == '':
            response.data = {'message': "Please Consider A Limit For Fetching Collection", 'data': []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        all_col = Collections.objects
        if all_col:
            for collection in all_col:
                last_volume = str(collection.last_volume)
                collection_volume_traded = 0
                nfts = [NFTs.objects.filter(id=nft_id) for nft_id in collection.nft_ids]
                nft_prices = []
                for nft in nfts:
                    nft_prices.append(nft.first().price)
                    total_sucessfull_price = 0
                    for price_history in nft.first().price_history:
                        total_sucessfull_price+=float(price_history.price)
                    collection_volume_traded+=total_sucessfull_price
                if collection_volume_traded != last_volume:
                    last_volume = collection_volume_traded
                floor_price = min(nft_prices) if len(nft_prices) > 0 else 0
                updated_col = Collections.objects(id=collection.id).update(__raw__={'$set': {'updated_at':datetime.datetime.now(), 'floor_price': str(floor_price), 'volume': str(collection_volume_traded), 'last_volume': str(last_volume)}})
                if not updated_col:
                    response.data = {'message': "Could Not Update Collection Floor Price Before Fetching It", 'data': []}
                    response.status_code = HTTP_200_OK
                    return response
            collections = Collections.objects[int(from_off):int(to_off)]
            cols = json.loads(collections.to_json())
            for col in cols:
                payload = dict(wallet_address=col["creator"])
                # r = requests.post(local_user_verify, data=payload)
                r = requests.post(user_verify, data=payload)
                if not r.status_code==200:
                    response.data = {"message": "User Not Verified", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
                if r.status_code == 200:
                    data = r.json()
                    username = data['data']['username']
                col['username'] = username
            response.data = {'message': "All NFT Collection Fetched Successfully", 'data': json.loads(collections.to_json())}
            response.status_code = HTTP_200_OK
            return response
        response.data = {"message": "No NFT Collection Found", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])              
    def get_collection_nfts(request):
        response = Response()
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        else:
            col_id = request.data['collection_id']
            from_off = request.data['from']
            to_off = request.data['to']
            col = Collections.objects(id=col_id).first()
            if not col:
                response.data = {"message": "No Collections Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            else:
                nfts = []
                l = len(col.nft_ids)
                if not l>0:
                    response.data = {"message": "No NFT Found For This Collection", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response
                if l>0:
                    for nft_id in col.nft_ids:
                        nft = NFTs.objects(id=nft_id).first()
                        ##############################
                        #### Added By: @wildonion ####
                        ##############################
                        properties = defaultdict(int)
                        for p in nft.extra:
                            key = p.name, p.value
                            properties[key] += 1
                        updated_nft_properties = [{'name': name, 'value': value, 'rarity': ((qty/len(col.nft_ids)) * 100)} for (name, value), qty in properties.items()]
                        updated_extra_list = [Property(name=p['name'], value=p['value'], rarity=p['rarity']) for p in updated_nft_properties]
                        e = len(updated_extra_list)
                        nft.extra = []
                        for i in range(e):
                            ex = Property(name=updated_extra_list[i]['name'], value=updated_extra_list[i]['value'], rarity=updated_extra_list[i]['rarity'])
                            nft.extra.append(ex)
                        nft.save()
                        NFTs.objects(id=nft_id).update(__raw__={'$set': {'updated_at': datetime.datetime.now()}})
                        ##############################
                        #### Ended By: @wildonion ####
                        ##############################
                        nft = json.loads(nft.to_json())
                        payload = dict(wallet_address=col.creator)
                        r = requests.post(user_verify, data=payload)
                        username = "" 
                        if r.status_code==200:
                            username = r.json()['data']['username']
                            if "avatar_path" in r.json()['data']:
                                avatar_path = r.json()['data']['avatar_path']
                            else:
                                avatar_path = ""
                        d = dict(collection_creator_username=username,
                                collection_creator_avatar=avatar_path)
                        nft["collection_info"] = d
                        nfts.append(nft)
                    if not len(nfts)>0:
                        response.data = {"message": "No NFTs Found For This Collection", "data": []}
                        response.status_code = HTTP_200_OK
                        return response
                    response.data = {"message": "Fetched Successfully", "data": nfts[int(from_off):int(to_off)]}
                    response.status_code = HTTP_200_OK
                    return response

    @api_view(['POST'])         
    def collection_mint(request):
        response = Response()
        col_id = request.data['collection_id']
        if Collections.objects(id=col_id):
            Collections.objects(id=col_id).update(__raw__={'$set': {'minted_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}})
            col = Collections.objects(id=col_id).first()
            response.data = {"message": "Minted Successfully", "data": json.loads(col.to_json())}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "NFT Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])               
    def load_collection(request):
        response = Response()
        from_off = request.data['from']
        to_off = request.data['to']
        cols = Collections.objects.order_by('-created_at')
        cols = cols[int(from_off):int(to_off)]
        if cols:
            response.data = {"message": "Fetched Successfully", "data": json.loads(cols.to_json())}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])            
    def verify_collection_creator(request):
        response = Response()
        col_id = request.data['collection_id']
        wallet_addr = request.data['wallet_address']
        col = Collections.objects(id=col_id).first()
        if col:
            if col.creator == wallet_addr:
                response.data = {"message": "Verified Successfully", "data": json.loads(col.to_json())}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "Creator Is Not Valid", "data": []}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
        else:
            response.data = {"message": "No Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])                             
    def load_price(request):
        response = Response()
        min_p = round(float(request.data['min']), 4)
        max_p = round(float(request.data['max']), 4)
        col_id = request.data['collection_id']
        col = Collections.objects(id=col_id).first()
        if col:
            nfts = []
            for i in col.nft_ids:
                nft = NFTs.objects(id=i).first()
                if min_p <= round(float(nft.price), 4) <= max_p:
                    serialized = json.loads(nft.to_json())
                    nfts.append(serialized)
            response.data = {"message": "Fetched Successfully", "data": nfts}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['GET']) 
    def sort_by_category(request):
        response = Response()
        categories = Collections.objects.values_list('category')
        categ = []
        if categories:
            for cat in categories:
                if cat not in categ:
                    categ.append(cat)
            response.data = {"message": "Fetched Successfully", "data": categ}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Categories Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])           
    def traded(request):
        response = Response()
        col_id = request.data['collection_id']
        col = Collections.objects(id=col_id).first()
        count = []
        if col:
            for i in col.nft_ids:
                owner_c = NFTs.objects(id=i).values_list('owners').count()
                count.append(owner_c)
            traded = sum(count)
            response.data = {"message": "Calculated Successfully", "data": traded}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Trades Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])                      
    def user_col(request):
        response = Response()
        wallet_address = request.data['wallet_address']
        if request.data:
            cols = Collections.objects(creator=wallet_address)
            if cols:
                response.data = {"message": "Fetched Successfully", "data": json.loads(cols.to_json())}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "No Collection Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
        else:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
        return response

    @api_view(['POST'])                           
    def verify_nft_col_activition(request):
        response = Response()
        nft_id = request.data['nft_id']
        nft_collection_id = request.data['nft_collection_id']
        if request.data:
            col = Collections.objects(id=nft_collection_id, nft_ids=nft_id)
            if col:
                response.data = {"message": "Collection Verified Successfully", "data": []}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "Collection Is Not Activated For Shop", "data": []}
                response.status_code = HTTP_403_FORBIDDEN
        else:
            response.data = {"message": "Enter Valid IDs", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
        return response

    @api_view(['POST'])                        
    def activate(request):
        response = Response()
        c_id = request.data['collection_id']
        state = request.data['activate/deactivate']
        if request.data:
            col = Collections.objects(id=c_id)
            if col:
                if state == "activate":
                    Collections.objects(id=c_id).update(__raw__={'$set': {'updated_at': datetime.datetime.now(), 'have_shop':True}})
                    response.data = {"message": "Shop Activated Successfully", "data": json.loads(col.to_json())}
                    response.status_code = HTTP_200_OK
                if state == "deactivate":
                    Collections.objects(id=c_id).update(__raw__={'$set': {'updated_at': datetime.datetime.now(), 'have_shop':False}})
                    response.data = {"message": "Shop Deactivated Successfully", "data": json.loads(col.to_json())}
                    response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "No Collection Found", "data":[]}
                response.status_code = HTTP_404_NOT_FOUND
        else:
            response.data = {"message": "Enter Valid Data", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
        return response

    @api_view(['POST'])
    def verify_collection_nft_current_owner(request):
        response = Response()
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
        else:
            col = Collections.objects(id=col_id).first()
            if col:
                nft_ids = col.nft_ids
            else:
                nft_ids = []
            l = len(nft_ids)
            res = []
            for i in range(l):
                if not NFTs.objects(id=nft_ids[i], current_owner=w_a):
                    pass
                else:
                    # j = json.loads(nfts.to_json())
                    res.append(nft_ids[i])
            l = len(res)
            if not l==0:
                response.data = {"message": "This Wallet Address Is Verified", "data":res}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "This Wallet Address Is Not Verified", "data":[]}
                response.status_code = HTTP_404_NOT_FOUND
        return response
    
    @api_view(['POST'])
    def minted_nfts(request):
        response = Response()
        col_id = request.data['collection_id']
        if not col_id:
            response.data = {"message": "Enter Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Collections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft_ids = col.nft_ids
        if not nft_ids:
            response.data = {"message": "This Collection Has No NFTs", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        minted_nfts = []
        for i in nft_ids:
            nft = NFTs.objects(id=i).first()
            if nft.current_owner:
                j_nft = json.loads(nft.to_json())
                minted_nfts.append(j_nft)
        if not len(minted_nfts)>0:
            response.data = {"message": "This Collection Has No Minted NFTs", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response            
        response.data = {"message": "Collection's Minted NFTs Fetched Successfully", "data": minted_nfts}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def likes(request):
        response = Response()
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not col_id:
            response.data = {"message": "Enter Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Collections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(wallet_address=w_a)
        # r = requests.post(local_user_verify, data=payload)
        r = requests.post(user_verify, data=payload)
        if not r.status_code==200:
            response.data = {"message": "User Not Verified", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        l = len(col.likes)
        likes = col.likes
        if not l>0:
            col.likes.append(w_a)
            col.save()
        temp = 0
        if l>0:
            for i in range(l):
                if likes[i]==w_a:
                    response.data = {"message": "This User Has Already Liked This Collection", "data": []}
                    response.status_code = HTTP_403_FORBIDDEN
                    return response
                if not likes[i]==w_a:
                    temp += 1
                    if temp==l:
                        col.likes.append(w_a)
                        col.save()
        col = Collections.objects(id=col_id).first()
        response.data = {"message": "Collection Likes Updated Successfully", "data": json.loads(col.to_json())}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def dislikes(request):
        response = Response()
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not col_id:
            response.data = {"message": "Enter Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Collections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(col.likes)
        likes = col.likes
        if not l>0:
            response.data = {"message": "Collection Already Has No Likes", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        temp = 0
        if l>0:
            for i in range(l):
                if likes[i]==w_a:
                    col.likes.remove(likes[i])
                    col.save()
                    col = Collections.objects(id=col_id).first()
                    response.data = {"message": "Collection Unliked Successfully", "data": json.loads(col.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                if not likes[i]==w_a:
                    temp += 1
                    if temp==l:
                        response.data = {"message": "This User Had Never Liked This Collection", "data": []}
                        response.status_code = HTTP_406_NOT_ACCEPTABLE
                        return response
                    
                    
                    
                    
                    
                    
###### ----------------------
###### Generative Collections
###### ----------------------
class GenCollectionApi:
    @api_view(['POST'])
    def create(request):
        response = Response()
        title = request.data['title']
        description = request.data['description']
        creator = request.data['creator']
        category = request.data['category']
        chain = request.data['chain']
        logo = request.FILES['logo']
        banner = request.FILES['banner_image']
        extra = request.data['extra']
        reveal = request.data['reveal']
        nft_count = request.data['nft_count']
        nft_mint = request.data['nft_mint']
        mint_per_wallet = request.data['mint_per_wallet']
        perpetual_royalties = request.data['perpetual_royalties']
        # (stdout, stderr) = request.data
        # print(stdout)
        if not title:
            response.data = {"message": "Enter Title", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not description:
            response.data = {"message": "Enter Description", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not category:
            response.data = {"message": "Enter Title", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not creator:
            response.data = {"message": "Enter Creator", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not reveal:
            response.data = {"message": "Enter Reveal", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not nft_mint:
            response.data = {"message": "Enter nft_mint", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if Gencollections.objects(title=title):
            response.data = {'message': "Generative NFT Collection With That Name Already Exists", 'data': title}
            response.status_code = HTTP_403_FORBIDDEN
            return response
        nft_count = int(nft_count)
        if not nft_count>0:
            response.data = {'message': "NFTs Of A Generative Collection Should Be Larger Than Zero", 'data': title}
            response.status_code = HTTP_403_FORBIDDEN
            return response
        if extra:
            extra = json.loads(extra)
        # logo_extension = os.path.splitext(logo.name)[1]
        col_folder = settings.MEDIA_ROOT
        if not os.path.exists(col_folder):
            os.mkdir(col_folder)
        logo_save_path = settings.MEDIA_ROOT + '/' + 'logo_' + str(datetime.datetime.now().timestamp()) + str(logo.name).replace(" ", "")
        with open(logo_save_path, "wb+") as f:
            for chunk in logo.chunks():
                f.write(chunk)
        # banner_extension = os.path.splitext(banner.name)[1]
        col_folder = settings.MEDIA_ROOT
        if not os.path.exists(col_folder):
            os.mkdir(col_folder)
        banner_save_path = settings.MEDIA_ROOT + '/' + 'banner_' + str(datetime.datetime.now().timestamp()) + str(banner.name).replace(" ", "")
        with open(banner_save_path, "wb+") as f:
            for chunk in banner.chunks():
                f.write(chunk)
        col = Gencollections(updated_at=datetime.datetime.now(),
                            title=title, description=description, creator=creator, chain=chain, category=category, logo_path=str(logo_save_path), banner_image_path=str(banner_save_path), extra=extra, created_at=datetime.datetime.now(), nft_owners_count=0)
        col.save()
        reveal = json.loads(reveal)
        rev = Reveal(reveal_time=reveal['reveal_time'], reveal_link=reveal['reveal_link'], start_mint_price=reveal['start_mint_price'], is_revealed=False)
        col.reveal.append(rev)
        col.save()
        if perpetual_royalties:
            perpetual_royalties = json.loads(perpetual_royalties)
            p = len(perpetual_royalties)
            perp = []
            for i in range(p):
                per = Perpetual_royalties(wallet_address=perpetual_royalties[i]['wallet_address'], royalty=perpetual_royalties[i]['royalty'])
                perp.append(per)
                col.default_perpetual_royalties.append(per)
            col.save()
            perp_l = len(perp)
            for i in range(nft_count):
                nft = NFTs(title=col.title+ f' #'+str(i), updated_at=datetime.datetime.now(), price=reveal['start_mint_price'], media=reveal['reveal_link'])
                for i in range(perp_l):
                    nft.perpetual_royalties.append(perp[i])
                nft.save()
                col.nft_ids.append(str(nft.id))
            col.save()
        if mint_per_wallet:
            mint_per_wallet = json.loads(mint_per_wallet)
            if mint_per_wallet['limitable'] == False:
                m_p_w = Mint_per_wallet(mint_count=0, limitable=False)
                col.mint_per_wallet.append(m_p_w)
                col.save()
            if mint_per_wallet['limitable'] == True:
                m_p_w = Mint_per_wallet(mint_count=int(mint_per_wallet['mint_count']), limitable=True)
                col.mint_per_wallet.append(m_p_w)
                col.save()
            # n = len(nft_mint)
            nft_mint = json.loads(nft_mint)
            mint = Nft_mint(start_mint=nft_mint['start_mint'], stop_mint=nft_mint['stop_mint'])
            col.nft_mint.append(mint)
            col.save()
        if col:
            response.data = {'message': "Generative NFT Collection Created Successfully", 'data': json.loads(col.to_json())}
            response.status_code = HTTP_201_CREATED
            return response

    @api_view(['POST'])             
    def edit(request):
        response = Response()
        col_id = request.data['collection_id']
        creator = request.data['creator']
        title = request.data['title']
        description = request.data['description']
        category = request.data['category']
        extra = request.data['extra']
        reveal = request.data['reveal']
        mint_per_wallet = request.data['mint_per_wallet']
        if not col_id:
            response.data = {"message": "Enter Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not creator:
            response.data = {"message": "Enter Creator Of Collection", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id, creator=creator).first()
        if not col:
            response.data = {"message": "Generative Collection With That Creator Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not title:
            title = col.title
        if title:
            if not title == col.title:
                if not Gencollections.objects(title=title):
                    title = title
                else:
                    response.data = {"message": "Generative NFT Collection With This Name Exists", "data": []}
                    response.status_code = HTTP_403_FORBIDDEN
                    return response
        if reveal:
            j = json.loads(reveal)
            rev = Reveal(reveal_time=j['reveal_time'], reveal_link=j['reveal_link'], start_mint_price=j['start_mint_price'])
            r = col.reveal
            if not r[0]['start_mint_price']==j['start_mint_price']:
                for i in col.nft_ids:
                    updated_nft = NFTs.objects(id=i).update(__raw__={'$set': {'price':j['start_mint_price']}})
                    if not updated_nft:
                        response.data = {'message': "NFTs Of Generative NFT Collection Could Not Be Updated Successfully", 'data': []}
                        response.status_code = HTTP_406_NOT_ACCEPTABLE
                        return response
            col.reveal = []
            col.reveal.append(rev)
            col.save()
        if mint_per_wallet:
            j = json.loads(mint_per_wallet)
            m_p_w = Mint_per_wallet(mint_count=j['mint_count'], limitable=j['limitable'])
            col.mint_per_wallet = []
            col.mint_per_wallet.append(m_p_w)
            col.save()
        if not len(mint_per_wallet)==0:
            mint_per_wallet == col.mint_per_wallet
        # if nft_mint:
        #     col.nft_mint=[]
        #     nft_mint = json.loads(nft_mint)
        #     mint = Nft_mint(start_mint=nft_mint['start_mint'], stop_mint=nft_mint['stop_mint'])
        #     col.nft_mint.append(mint)
        #     col.save()
        if not extra:
            extra = col.extra
        if extra:
            extra = json.loads(extra)
        if not category:
            category = col.category
        # if not total_mint_cost:
        #     total_mint_cost = col.total_mint_cost
        check_update = Gencollections.objects(id=col_id).update(__raw__={'$set': {'title': title, 'category': category, 'description': description, 'extra':extra, 'updated_at':datetime.datetime.now()}})
        if check_update:
            updated_col = Gencollections.objects(id=col_id)
            response.data = {'message': "Generative NFT Collection Updated Successfully", 'data': json.loads(updated_col.to_json())}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])          
    def get(request):
        response = Response()
        col_id = request.data['collection_id']
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Generative NFT Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if not col.views:
            col.views = 0
        col.views += 1
        col.save()
        col = Gencollections.objects(id=col_id).first()
        response.data = {'message': "Generative Collection And Its NFT Owners' Counts Fetched Successfully", 'data': json.loads(col.to_json())}
        response.status_code = HTTP_200_OK
        return response
    
    
    ##############################
    #### Added By: @wildonion ####
    ##############################
    # NOTE - trending collections is based on the whole price 
    #        number of all successfully completed NFT trades 
    #        for a specific time period. 
    @api_view(['POST'])
    def get_trendings(request):
        response = Response()
        when = request.data["when"] 
        collections = Gencollections.objects(created_at__lte=when)
        collection_infos = []
        if collections:
            for collection in collections:
                collection_volume_traded = 0
                nfts = [NFTs.objects(id=nft_id) for nft_id in collection.nfts]
                nft_prices = []
                for nft in nfts:
                    nft_prices.append(nft.price)
                    total_sucessfull_price = 0
                    for price_history in nft.price_history:
                        total_sucessfull_price+=float(price_history.price)
                    collection_volume_traded+=total_sucessfull_price
                floor_price = min(nft_prices) if len(nft_prices) > 0 else 0 
                collection_infos.append({"collection": json.loads(collection.to_json()), 
                                        "floor_price": floor_price, 
                                        "volume": collection_volume_traded,
                                        })
            response.data = {'message': "All NFT Collection Fetched Successfully", 'data': collection_infos}
            response.status_code = HTTP_200_OK
            return response
        response.data = {"message": "No NFT Collection Found", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
        return response
    ##############################
    #### Ended By: @wildonion ####
    ##############################
    
    

    @api_view(['GET']) 
    def get_all(request):
        response = Response()
        all_col = Gencollections.objects
        if all_col:
            response.data = {'message': "All Generative NFT Collection Fetched Successfully", 'data': json.loads(all_col.to_json())}
            response.status_code = HTTP_200_OK
            return response
        response.data = {"message": "No Generative NFT Collection Found", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])              
    def get_collection_nfts(request):
        response = Response()
        col_id = request.data['collection_id']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "No Generative Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if col:
            nfts = []
            l = len(col.nft_ids)
            if not l>0:
                response.data = {"message": "No NFT Found For This Generative Collection", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if l>0:
                # nfts_prices = []
                for i in col.nft_ids:
                    nft = NFTs.objects(id=i).first()
                    d = json.loads(nft.to_json())
                    nfts.append(d)
                if not len(nfts)>0:
                    response.data = {"message": "No NFTs Found For This Generative Collection", "data": []}
                    response.status_code = HTTP_200_OK
                    return response
                response.data = {"message": "NFTs Of Generative Collection Fetched Successfully", "data": nfts}
                response.status_code = HTTP_200_OK
                return response

    @api_view(['POST'])         
    def collection_mint(request):
        response = Response()
        col_id = request.data['collection_id']
        if Gencollections.objects(id=col_id):
            Gencollections.objects(id=col_id).update(__raw__={'$set': {'minted_at': datetime.datetime.now(), 'updated_at': datetime.datetime.now()}})
            col = Gencollections.objects(id=col_id).first()
            response.data = {"message": "Minted Successfully", "data": json.loads(col.to_json())}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "Generative NFT Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])               
    def load_collection(request):
        response = Response()
        from_off = request.data['from']
        to_off = request.data['to']
        cols = Gencollections.objects.order_by('-created_at')
        cols = cols[int(from_off):int(to_off)]
        if cols:
            response.data = {"message": "Fetched Successfully", "data": json.loads(cols.to_json())}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Generative Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])            
    def verify_collection_creator(request):
        response = Response()
        col_id = request.data['collection_id']
        wallet_addr = request.data['wallet_address']
        col = Gencollections.objects(id=col_id).first()
        if col:
            if col.creator == wallet_addr:
                response.data = {"message": "Verified Successfully", "data": json.loads(col.to_json())}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "Creator Is Not Valid", "data": []}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
        else:
            response.data = {"message": "No Generative Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])                             
    def load_price(request):
        response = Response()
        min_p = round(float(request.data['min']), 4)
        max_p = round(float(request.data['max']), 4)
        col_id = request.data['collection_id']
        col = Gencollections.objects(id=col_id).first()
        if col:
            nfts = []
            for i in col.nft_ids:
                nft = NFTs.objects(id=i).first()
                if min_p <= round(float(nft.price), 4) <= max_p:
                    serialized = json.loads(nft.to_json())
                    nfts.append(serialized)
            response.data = {"message": "Fetched Successfully", "data": nfts}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Generative Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response
                
    @api_view(['POST'])                         
    def load_by_category(request):
        response = Response()
        cat = request.data['category']
        cols = Gencollections.objects(category=cat)
        if not cols:
            response.data = {"message": "No Generative Collections Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        response.data = {"message": "Fetched Successfully", "data": json.loads(cols.to_json())}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['GET']) 
    def sort_by_category(request):
        response = Response()
        categories = Gencollections.objects.values_list('category')
        categ = []
        if categories:
            for cat in categories:
                if cat not in categ:
                    categ.append(cat)
            response.data = {"message": "Fetched Successfully", "data": categ}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Categories Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])           
    def traded(request):
        response = Response()
        col_id = request.data['collection_id']
        col = Gencollections.objects(id=col_id).first()
        count = []
        if col:
            for i in col.nft_ids:
                owner_c = NFTs.objects(id=i).values_list('owners').count()
                count.append(owner_c)
            traded = sum(count)
            response.data = {"message": "Calculated Successfully", "data": traded}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No Trades Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

    @api_view(['POST'])                      
    def user_col(request):
        response = Response()
        wallet_address = request.data['wallet_address']
        if request.data:
            cols = Gencollections.objects(creator=wallet_address)
            if cols:
                response.data = {"message": "Fetched Successfully", "data": json.loads(cols.to_json())}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "No Generative Collection Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
        else:
            response.data = {"message": "Enter Valid Data", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
        return response

    @api_view(['POST'])                           
    def verify_nft_col_activition(request):
        response = Response()
        nft_id = request.data['nft_id']
        nft_collection_id = request.data['nft_collection_id']
        if request.data:
            col = Gencollections.objects(id=nft_collection_id, nft_ids=nft_id, have_shop=True)
            if col:
                response.data = {"message": "Generative Collection Verified Successfully", "data": []}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "Generative Collection Is Not Activated For Shop", "data": []}
                response.status_code = HTTP_403_FORBIDDEN
        else:
            response.data = {"message": "Enter Valid IDs", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
        return response

    @api_view(['POST'])                        
    def activate(request):
        response = Response()
        c_id = request.data['collection_id']
        state = request.data['activate/deactivate']
        if request.data:
            col = Gencollections.objects(id=c_id)
            if col:
                if state == "activate":
                    Gencollections.objects(id=c_id).update(__raw__={'$set': {'updated_at': datetime.datetime.now(), 'have_shop':True}})
                    response.data = {"message": "Shop Activated Successfully", "data": json.loads(col.to_json())}
                    response.status_code = HTTP_200_OK
                if state == "deactivate":
                    Gencollections.objects(id=c_id).update(__raw__={'$set': {'updated_at': datetime.datetime.now(), 'have_shop':False}})
                    response.data = {"message": "Shop Deactivated Successfully", "data": json.loads(col.to_json())}
                    response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "No Generative Collection Found", "data":[]}
                response.status_code = HTTP_404_NOT_FOUND
        else:
            response.data = {"message": "Enter Valid Data", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
        return response

    @api_view(['POST'])
    def verify_collection_nft_current_owner(request):
        response = Response()
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not request.data:
            response.data = {"message": "Enter Valid Data", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        else:
            col = Gencollections.objects(id=col_id).first()
            nft_ids = col.nft_ids
            l = len(nft_ids)
            res = []
            for i in range(l):
                if NFTs.objects(id=nft_ids[i], current_owner=w_a):
                    # j = json.loads(nfts.to_json())
                    res.append(nft_ids[i])
            l = len(res)
            if l==0:
                response.data = {"message": "This Wallet Address Is Not Verified", "data":[]}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            response.data = {"message": "This Wallet Address Is Verified", "data":res}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])
    def get_creator_gen(request):
        response = Response()
        w_a = request.data['creator']
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        cols = Gencollections.objects(creator=w_a)
        if not cols:
            response.data = {"message": "No Generative Collections Found For The Requested Creator", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        response.data = {"message": "Generative Collections Of The Requested Creator Fetched Successfully", "data":json.loads(cols.to_json())}
        response.status_code = HTTP_200_OK
        return response
        

    @api_view(['POST'])
    def nft_metadata(request):
        response = Response()
        col_id = request.data['collection_id']
        metadata = request.FILES['metadata']
        if not col_id:
            response.data = {"message": "Enter Generative Collection ID", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not metadata:
            response.data = {"message": "Enter NFTs Json File", "data":[]}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "No Generative Collection Found With This Collection ID", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        metadata_folder = settings.MEDIA_ROOT
        if not os.path.exists(metadata_folder):
            os.mkdir(metadata_folder)
        metadata_save_path = settings.MEDIA_ROOT + '/' + 'metadata_' + str(datetime.datetime.now().timestamp()) + str(metadata.name).replace(" ", "")
        with open(metadata_save_path, "wb+") as f:
            for chunk in metadata.chunks():
                f.write(chunk)
        with open(metadata_save_path) as json_file:
            metadata = json.load(json_file)
        metadata_list = metadata['nft_metadata']
        l = len(metadata_list)
        i = len(col.nft_ids)
        if not l>=i:
            if os.path.exists(metadata_save_path):
                os.remove(metadata_save_path)
            response.data = {"message": "The Number Of Json Elements In The Json File Can Not Be Less Than Generative Collection's NFTs", "data":[]}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        updated_col = Gencollections.objects(id=col_id).update(__raw__={'$set': {'updated_at': datetime.datetime.now(), 'metadata_save_path': str(metadata_save_path)}})
        if not updated_col:
            response.data = {"message": "Generative Collection Could Not Be Updated Successfully", "data":[]}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        updated_col = Gencollections.objects(id=col_id).first()
        if not updated_col:
            response.data = {"message": "Generative Collection Could Not Be Fetched Successfully", "data":[]}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        response.data = {"message": "Generative Collection Updated And Fetched Successfully", "data":json.loads(updated_col.to_json())}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POSt'])
    def get_metadata(request):
        response = Response()
        col_id = request.data['collection_id']
        if not col_id:
            response.data = {"message": "Enter Generative Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Generative Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        path = col.metadata_save_path
        if not path:
            response.data = {"message": "No Metadata Found For This Generative Collection", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        response.data = {"message": "MetaData Of Generative Collection Fetched Successfully", "data": path}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['GET'])
    def all_unrevealed_collection(request):
        response = Response()
        # r = requests.get(local_get_all_gen_col)
        r = requests.get(get_all_gen_col)
        if not r.status_code==200:
            response.data = {"message": "No Generative Collections Found", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(r.json()['data'])
        if not l>0:
            response.data = {"message": "No Generative Collections Found", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        data = r.json()['data']
        res = []
        for i in range(l):
            if data[i]['reveal'][0]['is_revealed'] == False:
                res.append(data[i])
        if not len(res)>0:
            response.data = {"message": "No Unrevealed Generative Collection Found", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        response.data = {"message": "Unrevealed Generative Collections Fetched Successfully", "data":res}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['GET'])
    def reveal(request):
        response = Response()
        # r = requests.get(local_all_unrev_gen_col)
        r = requests.get(all_unrev_gen_col)
        if not r.status_code==200:
            response.data = {"message": "No Unrevealed Generative Collections Found", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(r.json()['data'])
        if not l>0:
            response.data = {"message": "No Unrevealed Generative Collections Found", "data":[]}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        data = r.json()['data']
        res = []
        for i in range(l):
            if int(datetime.datetime.utcnow().timestamp()*1000) >= int(data[i]['reveal'][0]['reveal_time']):
                col_id = data[i]['_id']['$oid']
                updated_col = Gencollections.objects(id=col_id, reveal__is_revealed=False).update(set__reveal__S__is_revealed=True)
                if not updated_col:
                    response.data = {"message": "One Of Generative Collection's Reveal Status Could Not Update Successfully", "data": []}
                    response.status_code = HTTP_406_NOT_ACCEPTABLE
                    return response
                res.append(data[i])
                payload = dict(revealed_collection=col_id)
                # r = requests.post(local_assign_metadata, json=payload)
                r = requests.post(assign_metadata, data=payload)
                if not r.status_code==200:
                    response.data = {"message": "Could Not Assign Metadata To The NFTs", "data": []}
                    response.status_code = HTTP_406_NOT_ACCEPTABLE
                    return response
        if not len(res)>0:
            response.data = {"message": "None Of Generative Collections Were Ready To Reveal", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if len(res)>0:
            response.data = {"message": "Generative Collections Revealed Successfully", "data": res}
            response.status_code = HTTP_200_OK
            return response

    @api_view(['POST'])
    def assign_metadata(request):
        response = Response()
        revealed_col = request.data['revealed_collection']
        if not revealed_col:
            response.data = {"message": "Enter Generative Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        # revealed_col = json.dumps(rev_col)
        # revealed_col = json.loads(rev)
        col = Gencollections.objects(id=revealed_col).first()
        if not col:
            response.data = {"message": "Generative Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(collection_id=revealed_col)
        # r = requests.post(local_get_col_metadata, data=payload)
        r = requests.post(get_col_metadata, data=payload)
        if not r.status_code==200:
            response.data = {"message": "No Metadata Found For This Generative Collection", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        path = r.json()['data']
        with open(path) as json_file:
            metadata = json.load(json_file)
        metadata_list = metadata['nft_metadata']
        if not len(metadata_list)>0:
            response.data = {"message": "No Metadata Found In The Json File", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(collection_id=revealed_col)
        # r = requests.post(local_get_gen_minted_nfts, data=payload)
        r = requests.post(get_gen_minted_nfts, data=payload)
        if not r.status_code==200:
            response.data = {"message": "No Minted NFTs Found For This Generative Collection", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        resp = r.json()['data']
        l = len(r.json()['data'])
        rand = random.sample(metadata_list, l)
        res = []
        for i in range(l):
            nft_id = resp[i]['_id']['$oid']
            nft = NFTs.objects(id=nft_id).first()
            updated_nft = NFTs.objects(id=nft_id).update(__raw__={'$set': {'title': rand[i]['title'], 'description': rand[i]['description'], 'media':rand[i]['media'], 'updated_at': datetime.datetime.now()}})
            if not updated_nft:
                response.data = {"message": "NFTs Could Not Be Updated Successfully", "data": []}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
                return response
            l_e = len(rand[i]['extra'])
            r_i = rand[i]
            if l_e>0:
                for i in range(l_e):
                    # extra_i = json.loads(r_i['extra'][i])
                    ex = Property(name=r_i['extra'][i]['name'], value=r_i['extra'][i]['value'])
                    nft.extra.append(ex)
                nft.save()
            nft = NFTs.objects(id=nft_id).first()
            j_nft = json.loads(nft.to_json())
            nft_info = {
                "token_id": str(nft_id),
                "metadata": {
                    "title":j_nft["title"],
                    "description":j_nft["description"],
                    "extra":json.dumps(j_nft['extra']),
                    "media":j_nft["media"],
                    "reference":json.dumps(j_nft["reference"]),
                    "issued_at":int(j_nft["issued_at"]),
                    "updated_at":int(j_nft["updated_at"]["$date"])
                }
            }
            a = json.dumps(nft_info)
            b = json.loads(a)
            res.append(b)
        metadata_folder = settings.MEDIA_ROOT
        if not os.path.exists(metadata_folder):
            os.mkdir(metadata_folder)
        metadata_save_path = settings.MEDIA_ROOT+ '/' + 'metadata_' + str(datetime.datetime.now().timestamp()) + 'metadata.json'
        with open(metadata_save_path, 'w') as metadata_file:
            json.dump(res, metadata_file)
        updated_col = Gencollections.objects(id=revealed_col).update(__raw__={'$set': {'metadata_save_path': str(metadata_save_path), 'updated_at': datetime.datetime.now()}})
        if not updated_col:
            response.data = {"message": "Generative Collection's Metadata File Could Not Update Successfully", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        response.data = {"message": "Minted NFTs Of Generative Collection Revealed Randomly And Successfully", "data": res}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def minted_nfts(request):
        response = Response()
        col_id = request.data['collection_id']
        if not col_id:
            response.data = {"message": "Enter Generative Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Generative Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        nft_ids = col.nft_ids
        if not nft_ids:
            response.data = {"message": "This Generative Collection Has No NFTs", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        minted_nfts = []
        for i in nft_ids:
            nft = NFTs.objects(id=i).first()
            if nft.current_owner:
                j_nft = json.loads(nft.to_json())
                minted_nfts.append(j_nft)
        if not len(minted_nfts)>0:
            response.data = {"message": "This Generative Collection Has No Minted NFTs", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response            
        response.data = {"message": "Generative Collection's Minted NFTs Fetched Successfully", "data": minted_nfts}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def likes(request):
        response = Response()
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not col_id:
            response.data = {"message": "Enter Generative Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Generative Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        payload = dict(wallet_address=w_a)
        # r = requests.post(local_user_verify, data=payload)
        r = requests.post(user_verify, data=payload)
        if not r.status_code==200:
            response.data = {"message": "User Not Verified", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        l = len(col.likes)
        likes = col.likes
        if not l>0:
            col.likes.append(w_a)
            col.save()
        temp = 0
        if l>0:
            for i in range(l):
                if likes[i]==w_a:
                    response.data = {"message": "This User Has Already Liked This Generative Collection", "data": []}
                    response.status_code = HTTP_403_FORBIDDEN
                    return response
                if not likes[i]==w_a:
                    temp += 1
                    if temp==l:
                        col.likes.append(w_a)
                        col.save()
        col = Gencollections.objects(id=col_id).first()
        response.data = {"message": "Generative Collection Likes Updated Successfully", "data": json.loads(col.to_json())}
        response.status_code = HTTP_200_OK
        return response

    @api_view(['POST'])
    def dislikes(request):
        response = Response()
        col_id = request.data['collection_id']
        w_a = request.data['wallet_address']
        if not col_id:
            response.data = {"message": "Enter Generative Collection ID", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        if not w_a:
            response.data = {"message": "Enter WalletAddress", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        col = Gencollections.objects(id=col_id).first()
        if not col:
            response.data = {"message": "Generative Collection Not Found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        l = len(col.likes)
        likes = col.likes
        if not l>0:
            response.data = {"message": "Generative Collection Already Has No Likes", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        temp = 0
        if l>0:
            for i in range(l):
                if likes[i]==w_a:
                    col.likes.remove(likes[i])
                    col.save()
                    col = Gencollections.objects(id=col_id).first()
                    response.data = {"message": "Generative Collection Unliked Successfully", "data": json.loads(col.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                if not likes[i]==w_a:
                    temp += 1
                    if temp==l:
                        response.data = {"message": "This User Had Never Liked This Generative Collection", "data": []}
                        response.status_code = HTTP_406_NOT_ACCEPTABLE
                        return response
                    
###### ----------------------
######      Search APIs
###### ----------------------          
class SearchApi:
    
    @api_view(['POST'])
    def search(request):
        response = Response()
        phrase = request.data['phrase']
        from_off = request.data['from']
        to_off = request.data['to']
        if not phrase:
            response.data = {"message": "Enter A Valid Data To Be Searched", "data": []}
            response.status_code = HTTP_400_BAD_REQUEST
            return response
        res = []
        cols = Collections.objects(__raw__={'$or': [{'title': {'$regex' : phrase}}]})[int(from_off):int(to_off)]
        if cols:
            j_cols = json.loads(cols.to_json())
            if len(j_cols)>0:
                d_cols = dict(collections=j_cols)
                res.append(d_cols)
            if not len(j_cols)>0:
                pass
        nfts = NFTs.objects(__raw__={'$or': [{'title': {'$regex' : phrase}}]})[int(from_off):int(to_off)]
        if nfts:
            j_nfts = json.loads(nfts.to_json())
            if len(j_nfts)>0:
                d_nfts = dict(nfts=j_nfts)
                for n in range(len(d_nfts["nfts"])):
                    pipeline = [
                        {
                            "$match": {
                                "nft_ids": str(d_nfts["nfts"][n]["_id"]["$oid"])
                            }
                        }
                    ]
                    fetch_col = Collections.objects.aggregate(pipeline)
                    if fetch_col:
                        for col in fetch_col:
                            col_creator = col["title"]
                            d_nfts["nfts"][n]["collection_name"] = col_creator
                res.append(d_nfts)
            if not len(j_nfts)>0:
                pass
        payload = dict(phrase=phrase)
        r = requests.post(user_search, data=payload)
        if r.status_code==200:
            users = r.json()['data'][int(from_off):int(to_off)]
            if len(users) > 0:
                d_users = dict(users=users)
                res.append(d_users)
        response.data = {"message": "Results For The Requested Phrase Fetched Successfully", "data": res}
        response.status_code = HTTP_200_OK
        return response
     
    @api_view(['POST'])                         
    def load_by_category(request):
        response = Response()
        cat = request.data['category']
        from_off = request.data['from']
        to_off = request.data['to']
        res = []
        cols = Collections.objects(category=cat)
        if cols:
            for col in cols:
                j = json.loads(col.to_json())
                payload = dict(wallet_address=j["creator"])
                # r = requests.post(local_user_verify, data=payload)
                r = requests.post(user_verify, data=payload)
                if not r.status_code==200:
                    response.data = {"message": "User Not Verified", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
                if r.status_code == 200:
                    data = r.json()
                    username = data['data']['username']
                j['username'] = username
                res.append(j)
        if not len(res)>0:
            response.data = {"message": "No Collection/ Generative Collection Found For This Category", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        if len(res)>0:
            response.data = {"message": "Fetched Successfully", "data": res[int(from_off):int(to_off)]}
            response.status_code = HTTP_200_OK
            return response
        
        
##############################
#### Added By: @wildonion ####
##############################
###### --------------------------
######    Shopping Basket APIs
###### --------------------------
# NOTE - batch transfer and purchase
#        must be done on contract side
#        using ERC1155
class BasketApi:

    @api_view(['POST'])
    def register(request):
        response = Response()
        if "buyer_info" in request.data:
            buyer_info = request.data["buyer_info"]
            new_bi = Basket_Buyer_Info(wallet_address=buyer_info["wallet_address"], username=buyer_info["username"], buyer_id=buyer_info["buyer_id"])
            find_basket = Basket.objects(buyer_info=new_bi).first()
            if find_basket and find_basket.tx_hash == "":
                response.data = {"message": "This Buyer Has Already An Unpurchased Basket Try To Add NFT To It Or Purchase It", "data": json.loads(find_basket.to_json())}
                response.status_code = HTTP_200_OK
                return response        
            else:
                basket = Basket(nfts=[], buyer_info=buyer_info, total_price="", tx_hash="", purchased_at="")
                basket.save()
                response.data = {"message": "Basket Generated Successfully", "data": json.loads(basket.to_json())}
                response.status_code = HTTP_201_CREATED
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response

    @api_view(['POST'])
    def add(request):
        response = Response()
        if "nft_info" in request.data and "basket_id" in request.data:
            nft_info = request.data["nft_info"]
            basket_id = request.data["basket_id"]
            nft_id = nft_info[0]['nft_id']
            basket_info = Basket.objects(id=basket_id).first()            
            is_found = False
            if basket_info:
                new_updated_nfts = []
                nfts = basket_info.nfts
                for nft in nfts:
                    if nft["nft_id"] == str(nft_id):
                        nft["quantity"] += 1
                        is_found = True
                        break
                    basket_info.nfts.append(
                            Basket_NFT_Info(nft_id=nft['nft_id'], 
                                            media=nft['media'], 
                                            title=nft['title'], 
                                            description=nft['description'], 
                                            price=nft['price'],
                                            copies=nft['copies'],
                                            quantity=int(nft['quantity'])
                                            )
                    )
                basket_info.save()
                if is_found:    
                    basket_info = Basket.objects(id=basket_id).first()            
                    response.data = {"message": "NFT Increamented Successfully To The Basket", "data": json.loads(basket_info.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                
                else:
                    ni = Basket_NFT_Info(nft_id=nft_info[0]['nft_id'], 
                                            media=nft_info[0]['media'], 
                                            title=nft_info[0]['title'], 
                                            description=nft_info[0]['description'], 
                                            price=nft_info[0]['price'],
                                            copies=nft_info[0]['copies'],
                                            quantity=int(nft_info[0]['quantity'])
                                        )
                    basket_info.nfts.append(ni)
                    basket_info.save()
                    response.data = {"message": "NFT Added Successfully To The Basket", "data": json.loads(basket_info.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    @api_view(['POST'])
    def add_q(request):
        response = Response()
        if "nft_id" in request.data and "basket_id" in request.data:
            nft_id = request.data["nft_id"]
            basket_id = request.data["basket_id"]
            is_found = False
            basket_info = Basket.objects(id=basket_id).first()
            if basket_info:
                nfts = basket_info.nfts
                new_updated_nfts = []
                for nft in nfts:
                    if nft["nft_id"] == str(nft_id): 
                        if nft["copies"] > 0 and nft["quantity"] < nft["copies"]:
                            nft["quantity"] += 1
                        is_found = True
                        break
                    basket_info.nfts.append(
                        Basket_NFT_Info(nft_id=nft['nft_id'], 
                                        media=nft['media'], 
                                        title=nft['title'], 
                                        description=nft['description'], 
                                        price=nft['price'],
                                        copies=nft['copies'],
                                        quantity=int(nft['quantity'])
                                        )
                    )
                basket_info.save()
                if is_found:
                    basket_info = Basket.objects(id=basket_id).first()          
                    response.data = {"message": "NFT Increamented Successfully To The Basket", "data": json.loads(basket_info.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                else:
                    response.data = {"message": "No NFT Found In Basket", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    @api_view(['POST'])
    def remove_q(request):
        response = Response()
        if "nft_id" in request.data and "basket_id" in request.data:
            nft_id = request.data["nft_id"]
            basket_id = request.data["basket_id"]
            is_found = False
            basket_info = Basket.objects(id=basket_id).first()
            if basket_info:
                new_updated_nfts = []
                nfts = basket_info.nfts
                for nft in nfts:
                    if nft["nft_id"] == str(nft_id):
                        q = int(nft["quantity"]) 
                        if nft["copies"] > 0 and nft["quantity"] > 1:
                            nft["quantity"] -= 1
                        is_found = True
                        break
                    basket_info.nfts.append(
                        Basket_NFT_Info(nft_id=nft['nft_id'], 
                                        media=nft['media'], 
                                        title=nft['title'], 
                                        description=nft['description'], 
                                        price=nft['price'],
                                        copies=nft['copies'],
                                        quantity=int(nft['quantity'])
                                        )
                    )
                basket_info.save() 
                if is_found:
                    basket_info = Basket.objects(id=basket_id).first()          
                    response.data = {"message": "NFT Decreamented Successfully To The Basket", "data": json.loads(basket_info.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                else:
                    response.data = {"message": "No NFT Found In Basket", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response

    @api_view(["POST"])
    def get(request):
        response = Response()
        if "basket_id" in request.data:
            basket_id = request.data["basket_id"]
            basket_info = Basket.objects(id=basket_id).first()
            if basket_info:
                nfts = basket_info.nfts
                latest_nft_info = []
                for nft in nfts: # we're fetching the latest nft from its collection since it might be changed  
                    nft_info = NFT.objects(id=nft.nft_id).first()
                    all_nft_info_json = json.loads(nft_info)
                    needed_nft_info_json = {"nft_id": all_nft_info_json["id"], "media": all_nft_info_json["media"], 
                                            "title": all_nft_info_json["title"], "description": all_nft_info_json["description"],
                                            "price": all_nft_info_json["price"], 
                                            "copies": all_nft_info_json["copies"]} 
                    latest_nft_info.append(needed_nft_info_json)
                json_basket_info = json.loads(basket_info.to_json())
                json_basket_info["nfts"] = latest_nft_info
                response.data = {"message": "Basket Fetched Successfully", "data": json_basket_info}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
    @api_view(['POST'])
    def remove(request):
        response = Response()
        if "nft_info" in request.data and "basket_id" in request.data:
            nft_info = request.data["nft_info"]
            basket_id = request.data["basket_id"]
            basket_info = Basket.objects(id=basket_id).first()
            if basket_info:
                for nft in basket_info.nfts:
                    if nft.nft_id == nft_info["nft_id"]:
                        basket_info.nfts.remove(nft)
                basket_info.save()
                response.data = {"message": "NFT Removed Successfully From The Basket", "data": json.loads(basket_info.to_json())}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    @api_view(['POST'])
    def remove_all(request):
        response = Response()
        if "basket_id" in request.data:
            basket_id = request.data["basket_id"]
            basket_info = Basket.objects(id=basket_id).delete()
            if basket_info:
                response.data = {"message": "Basket Removed Successfully", "data": []}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
    @api_view(['POST'])
    def purchase(request): ## this method will be called on successul purchase from the front-end
        response = Response()
        if "basket_id" in request.data:
            basket_id = request.data["basket_id"]
            tx_hash = request.data["tx_hash"]
            purchased_at = request.data["purchased_at"]
            total_price = request.data["total_price"]
            basket_info = Basket.objects(id=basket_id).first()
            if basket_info:
                basket_info.tx_hash = str(tx_hash)
                basket_info.purchased_at = purchased_at
                basket_info.total_price = total_price
                basket_info.save()
                response.data = {"message": "Basket Purchased Successfully", "data": json.loads(basket_info.to_json())}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Basket Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
##############################
#### Ended By: @wildonion ####
##############################



##############################
#### Added By: @wildonion ####
##############################
###### --------------------------
######      Watchlist APIs
###### --------------------------
class WatchlistApi:

    @api_view(['POST'])
    def add(request):
        response = Response()
        if "user_id" in request.data and "collection_id" in request.data:
            user_id = request.data["user_id"]
            collection_id = request.data["collection_id"]
            find_wl = Watchlist.objects(user_id=user_id).first()
            if find_wl:
                is_col_id_list = find_wl.collection_ids.count(collection_id)
                if is_col_id_list:
                    response.data = {"message": "Already Added To WatchList", "data": json.loads(find_wl.to_json())}
                    response.status_code = HTTP_200_OK
                    return response
                else:         
                    find_wl.collection_ids.append(str(collection_id))
                    find_wl.save() 
                    response.data = {"message": "Added To WatchList", "data": []}
                    response.status_code = HTTP_201_CREATED
                    return response        
            else:
                collection_ids = []
                collection_ids.append(str(collection_id))
                watchlist = Watchlist(collection_ids=collection_ids, user_id=user_id)
                watchlist.save()
                response.data = {"message": "Created WatchList", "data": json.loads(watchlist.to_json())}
                response.status_code = HTTP_201_CREATED
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
    @api_view(['POST'])
    def get(request):
        response = Response()
        if "user_id" in request.data:
            user_id = request.data["user_id"]
            find_wl = Watchlist.objects(user_id=user_id).first()
            if find_wl:
                collections = []
                for collection_id in find_wl.collection_ids:
                    collection = Collections.objects(id=collection_id).first()
                    last_volume = str(collection.last_volume)
                    collection_volume_traded = 0
                    nfts = [json.loads(NFTs.objects.filter(id=nft_id).to_json()) for nft_id in collection.nft_ids]
                    nft_prices = []
                    for nft in nfts:
                        nft_prices.append(nft[0]["price"])
                        total_sucessfull_price = 0
                        for price_history in nft[0]["price_history"]:
                            total_sucessfull_price+=float(price_history["price"])
                        collection_volume_traded+=total_sucessfull_price
                    if collection_volume_traded != last_volume:
                        last_volume = collection_volume_traded
                    floor_price = min(nft_prices) if len(nft_prices) > 0 else 0
                    updated_col = Collections.objects(id=collection.id).update(__raw__={'$set': {'updated_at':datetime.datetime.now(), 'floor_price': str(floor_price), 'volume': str(collection_volume_traded), 'last_volume': str(last_volume)}})
                    collection = Collections.objects(id=collection_id).first()
                    
                    col_info = Collections.objects.filter(id=collection.id)
                    col = json.loads(col_info.first().to_json())
                    json_nfts = []
                    for nft in nfts:
                        json_nfts.append(nft[0])
                    col['nfts'] = json_nfts
                    col['wl_id'] = str(find_wl.id)
                    collections.append(col)                
                response.data = {"message": "User Watchlist Collections Fetched Successfully", "data": collections}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Watchlist Found For This User", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response               
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    @api_view(['POST'])
    def remove(request):
        response = Response()
        if "watchlist_id" in request.data:
            watch_list_id = request.data["watchlist_id"]
            collection_id = request.data["collection_id"]
            wl_info = Watchlist.objects(id=watch_list_id).first()
            if wl_info:
                wl_info.collection_ids.remove(collection_id)
                wl_info.save()
                response.data = {"message": "Collection Removed Successfully From The Watchlist", "data": json.loads(wl_info.to_json())}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Watchlist Found With This Id", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
##############################
#### Ended By: @wildonion ####
##############################





##############################
#### Added By: @wildonion ####
##############################
###### --------------------------
######      Featured APIs
###### --------------------------
class FeaturedApi:

    @api_view(['POST'])
    def create(request):
        response = Response()
        if "title" in request.data and "description" in request.data and "nft_ids" in request.data and "user_id" in request.data:
            title = request.data["title"]
            description = request.data["description"]
            nft_ids = request.data["nft_ids"]
            user_id = request.data["user_id"]
            if nft_ids and title and description and user_id:
                ids = []
                nft_ids = json.loads(nft_ids)
                n = len(nft_ids)
                if not n==0:
                    for i in range(n):
                        id_ = nft_ids[i]
                        ids.append(id_)
                f = Featured(title=title, description=description, nft_ids=ids, user_id=str(user_id))
                f.save()
                response.data = {"message": "New Featured Created Successfully", "data": []}
                response.status_code = HTTP_200_OK
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
    @api_view(['POST'])
    def get_all_user_featureds(request):
        response = Response()
        if "user_id" in request.data:
            user_id = request.data["user_id"]
            find_featured = Featured.objects(user_id=str(user_id))
            if find_featured:
                data = []
                for f in find_featured:
                    nfts = [json.loads(NFTs.objects.filter(id=nft_id).to_json())[0] for nft_id in f.nft_ids]
                    f = json.loads(f.to_json())
                    del f["nft_ids"]
                    f.update({'nfts': nfts})     
                    data.append(f)       
                response.data = {"message": "User Watchlist Collections Fetched Successfully", "data": data}
                response.status_code = HTTP_200_OK
                return response
            else:
                response.data = {"message": "No Featured Found For This User", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response               
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    @api_view(['POST'])
    def remove(request):
        response = Response()
        if "featured_id" in request.data:
            featured_id = request.data["featured_id"]
            deleted_featured = Featured.objects(id=featured_id).delete()
            if deleted_featured:
                response.data = {'message': "Featured Deleted Successfully", 'data': []}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "Featured Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response


##############################
#### Added By: @wildonion ####
##############################
class NotifApi:
    @api_view(['POST'])
    def get_latest_notif(request):
        response = Response()
        wallet_address = request.data["wallet_address"] # float timestamp
        user_notif = UserNotif.objects(wallet_address=str(wallet_address)).first()
        if user_notif:
            response.data = {"message": "Latest Notif Fetched", "data": json.loads(user_notif.to_json())}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Please Register Notif", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
    
    @api_view(['POST'])
    def register_notif(request):
        response = Response()
        wallet_address = request.data["wallet_address"] # float timestamp
        item_sold = True if int(request.data["item_sold"]) == 1 else False # When someone purchased one of your items
        bid_activity = True if int(request.data["bid_activity"]) == 1 else False # When someone bids on one of your items
        price_change = True if int(request.data["price_change"]) == 1 else False # When an item you made an offer on changes in price
        auction_expiration = True if int(request.data["auction_expiration"]) == 1 else False# When a timed auction you created ends
        outbid = True if int(request.data["outbid"]) == 1 else False # When an offer you placed is exceeded by another user
        owned_item_updates = True if int(request.data["owned_item_updates"]) == 1 else False # When a significant update occurs for one of the items you have purchased on dortzio
        # successfull_purchase = request.data["successfull_purchase"] # Occasional updates from the dortzio team
        min_bid_tresh = request.data["min_bid_tresh"] # Receive notifications only when you receive offers with a value greater than or equal to this amount of ETH.

        item_sold_notif_data = NotifData(is_active=item_sold, notifs=[])
        bid_activity_notif_data = NotifData(is_active=bid_activity, notifs=[])
        price_change_notif_data = NotifData(is_active=price_change, notifs=[])
        auction_expiration_notif_data = NotifData(is_active=auction_expiration, notifs=[])
        outbid_notif_data = NotifData(is_active=outbid, notifs=[])
        owned_item_updates_notif_data = NotifData(is_active=owned_item_updates, notifs=[])
        # successfull_purchase_notif_data = NotifData(is_active=item_sold, notifs=[])
        user_notif = UserNotif(wallet_address=wallet_address, 
                                item_sold=item_sold_notif_data,
                                bid_activity=bid_activity_notif_data,
                                price_change=price_change_notif_data,
                                auction_expiration=auction_expiration_notif_data,
                                outbid=outbid_notif_data,
                                owned_item_updates=owned_item_updates_notif_data,
                                # successfull_purchase=successfull_purchase_notif_data,
                                min_bid_tresh=str(min_bid_tresh))
        user_notif.save()
        response.data = {"message": "Notif Created", "data": json.loads(user_notif.to_json())}
        response.status_code = HTTP_201_CREATED
        return response
    
    @api_view(['POST'])
    def seen(request):
        response = Response()
        wallet_address = request.data["wallet_address"] # float timestamp
        notif_data_index = request.data["notif_index"]
        notif_data = request.data["notif_data"]
        
        user_notif = UserNotif.objects(wallet_address=wallet_address).first()
        
        if user_notif:
            if notif_data == "item_sold":
                user_notif.item_sold.notifs[int(notif_data_index)].seen = True
            if notif_data == "bid_activity":
                user_notif.bid_activity.notifs[int(notif_data_index)].seen = True
            if notif_data == "price_change":
                user_notif.price_change.notifs[int(notif_data_index)].seen = True
            if notif_data == "auction_expiration":
                user_notif.auction_expiration.notifs[int(notif_data_index)].seen = True
            if notif_data == "outbid":
                user_notif.outbid.notifs[int(notif_data_index)].seen = True
            if notif_data == "owned_item_updates":
                user_notif.owned_item_updates.notifs[int(notif_data_index)].seen = True
            user_notif.save()
            response.data = {"message": "Notif Seen", "data": json.loads(user_notif.to_json())}
            response.status_code = HTTP_201_CREATED
            return response
        else:
            response.data = {"message": "Please Register Notif", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
            return response
        
    @api_view(['POST'])
    def edit_notif(request):
        response = Response()
        wallet_address = request.data["wallet_address"]
        item_sold = True if int(request.data["item_sold"]) == 1 else False # When someone purchased one of your items
        bid_activity = True if int(request.data["bid_activity"]) == 1 else False # When someone bids on one of your items
        price_change = True if int(request.data["price_change"]) == 1 else False # When an item you made an offer on changes in price
        auction_expiration = True if int(request.data["auction_expiration"]) == 1 else False# When a timed auction you created ends
        outbid = True if int(request.data["outbid"]) == 1 else False # When an offer you placed is exceeded by another user
        owned_item_updates = True if int(request.data["owned_item_updates"]) == 1 else False # When a significant update occurs for one of the items you have purchased on dortzio
        # successfull_purchase = request.data["successfull_purchase"] # Occasional updates from the dortzio team
        min_bid_tresh = request.data["min_bid_tresh"] # Receive notifications only when you receive offers with a value greater than or equal to this amount of ETH.


        user_notif = UserNotif.objects(wallet_address=wallet_address).first()
        user_notif.item_sold.is_active = item_sold
        user_notif.bid_activity.is_active = bid_activity
        user_notif.price_change.is_active = price_change
        user_notif.auction_expiration.is_active = auction_expiration
        user_notif.outbid.is_active = outbid
        user_notif.owned_item_updates.is_active = owned_item_updates
        user_notif.min_bid_tresh = min_bid_tresh
        
        user_notif.save()
        response.data = {"message": "Notif Updated", "data": json.loads(user_notif.to_json())}
        response.status_code = HTTP_201_CREATED
        return response

##############################
#### Ended By: @wildonion ####
##############################