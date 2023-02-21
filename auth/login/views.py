


import datetime
import json
import os
import random
import subprocess
import time
from mongoengine import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
import requests
from django.conf import settings
from django.conf.urls.static import static
import requests
from .models import Users, Offers








##### ------------------
#####  constants routes
##### ------------------

get_user_nft=settings.GET_USER_NFT
edit_nft=settings.EDIT_NFT
owner_nft_offer=settings.OWNER_NFT_OFFERS
user_pend_offer=settings.USER_PENDING_OFFERS
get_offer=settings.GET_OFFER
update_offer_col_ms=settings.UPDATE_OFFER_COL_MS
update_offer_status=settings.UPDATE_OFFER_STATUS


##### -------------------
#####     User APIs 
##### -------------------

class UserApi:
    
    @api_view(['GET'])
    def index(request):
        response = Response()
        response.data = {'message': "Welcome To Auth", 'data': []}
        response.status_code = HTTP_200_OK
        return response


    ##### ------------ login api
    ##### ----------------------
    @api_view(['POST'])
    def login(request):
        response = Response()
        if request.data:
            wallet_address = request.data['wallet_address']
            user = Users.objects(user_id=wallet_address).first()
            if user:
                Users.objects(user_id=wallet_address).update(__raw__={'$set': {'last_connect': datetime.datetime.now()}})
                response.data = {"message": "Logged In Successfully", "data":  json.loads(user.to_json())}
                response.status_code = HTTP_200_OK
                return response
            else:
                user = Users(username=wallet_address, user_id=wallet_address, reg_date=datetime.datetime.now(), last_connect=datetime.datetime.now())
                user.save()
                response.data = {"message": "Signed up Successfully", "data": json.loads(user.to_json())}
                response.status_code = HTTP_201_CREATED
                return response
        else:
            response.data = {"message": "Please Enter A Valid Wallet Address"}
            response.status_code = HTTP_404_NOT_FOUND
            return response  
    
    
    
    ##### ------------ metadata edit api
    ##### ------------------------------
    @api_view(['POST'])
    def edit(request):
        response = Response()
        if request.data:
            user_id = request.data["id"] ### this is mongodb objectid
            description = request.data['description']
            extra = request.data["extra"]
            username = request.data["username"]
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            user = Users.objects(id=user_id).first()
            if not user:
                response.data = {"message": "No User Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response 
            if not description:
                description = user.description
            if not extra:
                extra = user.extra
            if extra:
                extra = json.loads(json.dumps(extra))
            if not username:
                username = user.username
            Users.objects(id=user_id).update(__raw__={'$set': {'description': description, 'extra':extra, 'username': username}})
            updated_user = Users.objects(id=user_id).first()
            if not updated_user:
                response.data = {'message': "Something Went Wrong", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            response.data = {'message': 'User Updated Successfully', "data": json.loads(updated_user.to_json())}   
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response


    ##### ------------ edit avatar api
    ##### ----------------------------
    @api_view(['POST'])
    def edit_avatar(request):
        response = Response()
        if request.data:
            user_id = request.data["id"] ### this is mongodb objectid
            avatar = request.FILES['avatar']
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            user = Users.objects(id=user_id).first()
            if not user:
                response.data = {"message": "No User Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response 
            avatar_folder = settings.MEDIA_ROOT
            if not os.path.exists(avatar_folder):
                os.mkdir(avatar_folder)
            avatar_save_path = settings.MEDIA_ROOT + '/' + 'avatar_' + str(datetime.datetime.now().timestamp()) + str(avatar.name).replace(" ", "")
            with open(avatar_save_path, "wb+") as f:
                for chunk in avatar.chunks():
                    f.write(chunk)
            updated_user = Users.objects(id=user_id).update(__raw__={"$set": {"last_connect": datetime.datetime.now(), 'avatar_path': str(avatar_save_path)}})
            if not updated_user: 
                response.data = {"message": "User Avatar Could Not Be Updated", "data": []}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
                return response
            response.data = {"message": "Avatar Updated Successfully", "data": []}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
    ##### ------------ edit banner api
    ##### ----------------------------
    @api_view(['POST'])
    def edit_banner(request):
        response = Response()
        if request.data:
            user_id = request.data["id"] ### this is mongodb objectid
            banner = request.FILES['banner']
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            user = Users.objects(id=user_id).first()
            if not user:
                response.data = {"message": "No User Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response 
            banner_folder = settings.MEDIA_ROOT
            if not os.path.exists(banner_folder):
                os.mkdir(banner_folder)
            banner_save_path = settings.MEDIA_ROOT + '/' + 'banner_' + str(datetime.datetime.now().timestamp()) + str(banner.name).replace(" ", "")
            with open(banner_save_path, "wb+") as f:
                for chunk in banner.chunks():
                    f.write(chunk)
            updated_user = Users.objects(id=user_id).update(__raw__={"$set": {"last_connect": datetime.datetime.now(), 'banner_path': str(banner_save_path)}})
            if not updated_user: 
                response.data = {"message": "User Banner Could Not Be Updated", "data": []}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
                return response
            response.data = {"message": "Banner Updated Successfully", "data": []}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    ##### ------------ get user api
    ##### -------------------------
    @api_view(['POST'])                                      
    def get_user(request):
        response = Response()
        if request.data:
            username = request.data['username']
            user = Users.objects(username=username).first()
            if not user:
                response.data = {"message": "No Such User", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            response.data = {"message": "User Fetched Successfully", "data": json.loads(user.to_json())}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
    ##### ------------ get users api
    ##### --------------------------
    @api_view(['GET'])
    def get_all_users(request):
        response = Response()
        if Users.objects:
            response.data = {"message": "Fetched Successfully", "data": json.loads((Users.objects.to_json()))}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No User", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response
    
    
    ##### ------------ verify user api
    ##### ----------------------------
    @api_view(["POST"])
    def verify_user(request): ### will check that the user is in db or not
        response = Response()
        if request.data:
            wallet_address = request.data["wallet_address"]
            if not wallet_address:
                response.data = {"message": "Enter Valid data", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            user = Users.objects(user_id=wallet_address).first()
            if not user:
                response.data = {"message": "No Such User", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            response.data = {"message": "User Verified Successfully", "data": json.loads(user.to_json())}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response 
    
    ##### ------------ nft_offers api
    ##### ---------------------------
    @api_view(['POST'])
    def nft_offers(request):
        response = Response()
        if request.data:
            current_owner = request.data["current_owner"]
            if not current_owner:
                response.data = {"message": "Enter Current Owner", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            payload = dict(current_owner=current_owner)
            request_to_market = requests.post(owner_nft_offer, data=payload)
            if not request_to_market.status_code == 200:
                response.data = {"message": "No Offer Found For This User", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            response.data = {"message": "Offers Fetched Successfully", "data": request_to_market.json()}
            response.status_code = HTTP_200_OK
            return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response 
        
    ##### ------------ add_offer api
    ##### ---------------------------
    @api_view(['POST'])
    def add_offer(request):
        response = Response()
        if request.data:
            offer = request.data['offer']
            if not offer:
                response.data = {"message": "Enter Offer", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            offer = json.loads(offer)
            sender = Users.objects(user_id=offer['from_wallet_address']).first()
            receiver = Users.objects(user_id=offer['to_wallet_address']).first()
            offer = Offers(nft_id=offer['nft_id'], nft_media=offer['nft_media'], nft_title=offer['nft_title'], from_wallet_address=offer['from_wallet_address'],  to_wallet_address=offer['to_wallet_address'], price=offer['price'], status=offer['status'])
            sender.offers.append(offer)
            sender.save()        
            receiver.offers.append(offer)
            receiver.save()
            response.data = {"message": "Offer Added Successfully", "data": json.loads(receiver.to_json())}
            response.status_code = HTTP_200_OK
            return response            
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response 


    ##### ------------ accept_decline_offer
    ##### ---------------------------------
    @api_view(['POST'])
    def acc_dec_offer(request):
        if request.data:
            response = Response()
            user_id = request.data['user_id'] #### this is the wallet address of the user since user_id and wallet_address are same
            offer = request.data['offer']
            acc_dec = request.data['status'] ### the status of an offer which might be accept or decline
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not offer:
                response.data = {"message": "Enter Offer", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not acc_dec:
                response.data = {"message": "Enter Satus", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not Users.objects(user_id=user_id): #### search by user_id which is the wallet address also
                response.data = {"message": "User Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            payload = dict(wallet_address=user_id)
            request_to_market = requests.post(get_user_nft, json=payload)
            if not request_to_market.status_code==200:
                response.data = {"message": "Currently This User Owns No NFT", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            user_nfts = request_to_market.json()['data']
            user_nft_count = len(user_nfts)
            any_error = False
            for i in range(user_nft_count):
                if not user_nfts[i]['_id']['$oid'] == offer[0]['nft_id']:
                    if i+1 == user_nft_count:
                        if any_error==False:
                            response.data = {"message": "User Does Not Own This NFT", "data": []}
                            response.status_code = HTTP_400_BAD_REQUEST
                            return response
                if user_nfts[i]['_id']['$oid'] == offer[0]['nft_id']:
                    any_error = True
            j_nft_id= offer[0]['nft_id']
            j_to_w_a = offer[0]['to_wallet_address']
            j_from_w_a = offer[0]['from_wallet_address']
            j_price = offer[0]['price']
            if any_error:
                off = json.dumps(offer[0])
                payload = dict(offer=offer)
                request_to_market = requests.post(get_offer, json=payload)
                if not request_to_market.status_code==200:
                    response.data = {"message": "Offer Not Found", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response
                payload = dict(offer=offer, status=acc_dec)
                request_to_market = requests.post(update_offer_status, data=payload)
                if not request_to_market.status_code==200:
                    response.data = {"message": "Offer's Status Could Not Be Updated Successfully", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
                payload = dict(offer=offer, status=acc_dec)
                request_to_market = requests.post(update_offer_col_ms, json=payload)
                if not request_to_market.status_code==200:
                    response.data = {"message": "Offer Updated But Could Not Be Updated On NFT Side", "data": []}
                    response.status_code = HTTP_400_BAD_REQUEST
                    return response
                payload = dict(nft_id=j_nft_id, current_owner=j_to_w_a, new_current_owner=j_from_w_a,title="", description="", expires_at="" , extra="", price=j_price, perpetual_royalties="", reference="", media="", price_history="", listings ="", approved_account_ids="")
                request_to_market = requests.post(edit_nft, data=payload)
                if not request_to_market.status_code==200:
                    response.data = {"message": "NFT Could Not Transfer Successfully", "data": []}
                    response.status_code = HTTP_406_NOT_ACCEPTABLE
                    return response
                payload = dict(offer=offer)
                request_to_market = requests.post(get_offer, json=payload)
                if not request_to_market.status_code==200:
                    response.data = {"message": "Offer Updated But Could Not Be Fetched To Be Shown", "data": []}
                    response.status_code = HTTP_200_OK
                    return response
                response.data = {"message": "Offer's State Updated Successfully", "data":  []}
                response.status_code = HTTP_200_OK
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        
        
    ##### ------------ update offer status
    ##### --------------------------------    
    @api_view(['POST'])
    def update_offer_status(request):
        response = Response()
        if request.data:
            offer = request.data['offer']
            status = request.data['status']
            if not offer:
                response.data = {"message": "Enter Valid Data", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            offer = json.loads(offer)
            if not Users.objects(user_id=offer['from_wallet_address']):      #Replacing "from_wallet_address" With "to_wallet_address" Causes To Update Receivers Offer Status
                response.data = {"message": "Sender Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if not Users.objects(user_id=offer['to_wallet_address']):
                response.data = {"message": "Receiver Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            receiver = Users.objects(user_id=offer['to_wallet_address']).first()
            sender = Users.objects(user_id=offer['from_wallet_address']).first()
            rec_o_l = len(receiver.offers)
            if not rec_o_l > 0:
                response.data = {"message": "No Offer Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if rec_o_l > 0:
                for i in range(rec_o_l):
                    if receiver.offers[i]['nft_id'] == offer['nft_id']:
                        if receiver.offers[i]['from_wallet_address'] == offer['from_wallet_address']:
                            if receiver.offers[i]['to_wallet_address'] == offer['to_wallet_address']:
                                if receiver.offers[i]['status'] == offer['status']:
                                    if receiver.offers[i]['price'] == offer['price']:
                                        receiver.offers[i]['status'] = status
                                        receiver.save()
            sen_o_l = len(sender.offers)
            if not rec_o_l > 0:
                response.data = {"message": "No Offer Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if sen_o_l > 0:
                res = []
                for i in range(sen_o_l):
                    if sender.offers[i]['nft_id'] == offer['nft_id']:
                        if sender.offers[i]['from_wallet_address'] == offer['from_wallet_address']:
                            if sender.offers[i]['to_wallet_address'] == offer['to_wallet_address']:
                                if sender.offers[i]['status'] == offer['status']:
                                    if sender.offers[i]['price'] == offer['price']:
                                        sender.offers[i]['status'] = status
                                        sender.save()
                                        j = json.loads(sender.offers[i].to_json())
                                        res.append(j)
                if not len(res) > 0:
                    response.data = {"message": "No Such Offer Found", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response  
                if len(res) > 0:          
                    response.data = {"message": "Offer Status Updated Successfully", "data": res}
                    response.status_code = HTTP_200_OK
                    return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
    
    ##### ------------ get all user offers
    ##### -------------------------------- 
    @api_view(['POST'])
    def get_user_all_offers(request):
        response = Response()
        if request.data:
            user_id = request.data['user_id'] #### wallet address
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not Users.objects(user_id=user_id):
                response.data = {"message": "User Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            user = Users.objects(user_id=user_id).first()
            offer_len = len(user.offers)
            if not offer_len > 0:
                response.data = {"message": "User Has No Offers", "data":[]}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if offer_len > 0:
                res = []
                for i in user.offers:
                    j = json.loads(i.to_json())
                    res.append(j)
                response.data = {"message": "Users' Offers Fetched Successfully", "data":res}
                response.status_code = HTTP_200_OK
                return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response

    ##### ------------ get all user waiting offers
    ##### ----------------------------------------
    @api_view(['POST'])
    def get_user_waiting_offers(request):
        response = Response()
        if request.data:
            user_id = request.data['user_id'] #### wallet address #### wallet address
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not Users.objects(user_id=user_id):
                response.data = {"message": "User Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            user = Users.objects(user_id=user_id).first()
            offer_len = len(user.offers)
            if not offer_len > 0:
                response.data = {"message": "User Has No Offers", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if offer_len > 0:
                offers = user.offers
                res = []
                for i in range(offer_len):
                    if offers[i]['status'] == 'waiting':
                        j = json.loads(offers[i].to_json())
                        res.append(j)
                if not len(res) > 0:
                    response.data = {"message": "User Has No Pending Offers", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response
                if len(res) > 0:
                    response.data = {"message": "Users' Pending Offers Fetched Successfully", "data": res}
                    response.status_code = HTTP_200_OK
                    return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response
        

    ##### ------------ get all user done offers
    ##### -------------------------------------
    @api_view(['POST'])
    def get_user_done_offers(request):
        response = Response()
        if request.data:
            user_id = request.data['user_id'] #### wallet address
            if not user_id:
                response.data = {"message": "Enter User ID", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            if not Users.objects(user_id=user_id):
                response.data = {"message": "User Not Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            user = Users.objects(user_id=user_id).first()
            offer_len = len(user.offers)
            if not offer_len > 0:
                response.data = {"message": "User Has No Offers", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if offer_len > 0:
                offers = user.offers
                res = []
                for i in range(offer_len):
                    if not offers[i]['status'] == 'waiting':
                        j = json.loads(offers[i].to_json())
                        res.append(j)
                if not len(res) > 0:
                    response.data = {"message": "User Has No Done Offers", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response
                if len(res) > 0:
                    response.data = {"message": "Users' Done Offers Fetched Successfully", "data": res}
                    response.status_code = HTTP_200_OK
                    return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response


    ##### ------------ get an offer info
    ##### ------------------------------
    @api_view(['POST'])
    def get_offer(request):
        response = Response()
        if request.data:
            offer = request.data['offer']
            if not offer:
                response.data = {"message": "Enter Offer", "data": []}
                response.status_code = HTTP_400_BAD_REQUEST
                return response
            offer = json.loads(offer)
            if not Users.objects(user_id=offer['to_wallet_address']):
                response.data = {"message": "No User Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            user = Users.objects(user_id=offer['to_wallet_address']).first()
            user_offer_list = len(user.offers)
            if not user_offer_list > 0:
                response.data = {"message": "No Offer Found", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
                return response
            if user_offer_list > 0:
                res = []
                for i in range(user_offer_list):
                    if  user.offers[i]['nft_id'] == offer['nft_id']:
                        if  user.offers[i]['from_wallet_address'] == offer['from_wallet_address']:
                            if  user.offers[i]['to_wallet_address'] == offer['to_wallet_address']:
                                if  user.offers[i]['status'] == offer['status']:
                                    if  user.offers[i]['price'] == offer['price']:
                                        j = json.loads( user.offers[i].to_json())
                                        res.append(j)
                if not len(res) > 0:
                    response.data = {"message": "No Offer Found", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                    return response  
                if len(res) > 0:          
                    response.data = {"message": "Offer Fetched Successfully", "data": res}
                    response.status_code = HTTP_200_OK
                    return response
        else:
            response.data = {"message": "Request Body Can't Be Empty", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
            return response