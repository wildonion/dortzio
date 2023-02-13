


import datetime
from mongoengine import * 




class Owners(EmbeddedDocument):
    owner_wallet_address = StringField()

class Perpetual_royalties(EmbeddedDocument):
    wallet_address = StringField()
    royalty = IntField()
    

class Basket_Buyer_Info(EmbeddedDocument):
    wallet_address = StringField()
    username = StringField()
    buyer_id = ObjectIdField(required=True)

class Basket_NFT_Info(EmbeddedDocument):
    nft_id = StringField()
    media = StringField()
    title = StringField(max_length=200)
    description = StringField()
    price = StringField(min_value=0)
    perpetual_royalties = ListField(EmbeddedDocumentField(Perpetual_royalties))
    copies = IntField(min_value=1)
    
    

class Price_history(EmbeddedDocument):
    owner_wallet_address = StringField()
    sold_at = StringField()
    price = StringField()

class Offers(EmbeddedDocument):
    status_choice = (('accepted', 'Accepted'),('waiting', 'Waiting'),('canceled','Canceled'))
    nft_id = StringField()
    nft_title = StringField()
    nft_media = StringField()
    from_wallet_address = StringField()
    to_wallet_address = StringField()
    price = StringField()
    status = StringField(choices=status_choice)

class Listings(EmbeddedDocument):
    from_wallet_address = StringField() #### the current owner
    nft_id = StringField()
    expiration = StringField()
    price = StringField()

class Asset_activity(EmbeddedDocument):
    event = StringField()
    expiration = StringField()
    price = StringField()
    receiver_id = StringField()
    from_wallet_address = StringField()
    date = StringField()

class Auction(EmbeddedDocument):
    nft_id = StringField()
    is_ended = BooleanField(default=False)
    start_time = StringField(min_length=1)
    duration = StringField(min_length=1)
    starting_price = StringField(min_value=0)
    reserve_price = StringField()
    include_reserve_price = BooleanField(default=False)
    bids = ListField(DictField())


class Property(EmbeddedDocument):
    name = StringField()
    value = StringField()
    rarity = IntField()
    
class Reveal(EmbeddedDocument):
    reveal_time = StringField()
    reveal_link = URLField()
    start_mint_price = StringField()     #Mint all Nfts of generative collection before reveal "with this price"
    is_revealed = BooleanField(default=False)


class Nft_mint(EmbeddedDocument):
    start_mint = StringField()
    stop_mint = StringField()
    
class Mint_per_wallet(EmbeddedDocument):
    mint_count = IntField(min_value=0)
    limitable = BooleanField(default=False)
    
    
class NFTs(Document):
    title = StringField(max_length=200)
    description = StringField()
    price = StringField(min_value=0)
    copies = IntField(min_value=1)
    issued_at = StringField()
    expires_at = StringField()
    updated_at = DateTimeField()
    extra = ListField(EmbeddedDocumentField(Property))
    reference = DictField(StringField(), default=dict)
    views = IntField(min_value=0)
    likes = ListField(StringField())
    current_owner = StringField() #### wallet address
    media = URLField()
    nft_image_path = StringField()      
    is_freezed = BooleanField()
    owners = ListField(EmbeddedDocumentField(Owners))                                                                                    #[{ "owner_wallet_address": WalletAddr, "royalty": UnsignedInt,}, ... ]
    perpetual_royalties = ListField(EmbeddedDocumentField(Perpetual_royalties))                            #[{"user_id": walletAddr, "royalty": UnsignedInt}, ...]
    offers = ListField(EmbeddedDocumentField(Offers))                                            #[{"from_wallet_address" : WalletAddr, "expiration": DateTime, "price": UnsignedInt}, ...]  FROM UI
    listings = ListField(EmbeddedDocumentField(Listings))                                         #[{"price" : UnsignedInt, "expiration": DateTime, "from_wallet_address": WalletAddr}, ...] FROM UI
    approved_account_ids = DictField(StringField(), default=dict)                                                              #{WalletAddr: UnsignedInt, anotherwalletaddr: int}   wallet_addresses which can sell on behalf of owner   FROM UI
    asset_activity = ListField(EmbeddedDocumentField(Asset_activity))                            #[{"event" : String, "price": UnsignedInt, "from_wallet_address": WalletAddr, "receiver_id": WalletAddr, "Date": DateTime}, ...] FROM UI
    price_history = ListField(EmbeddedDocumentField(Price_history))                                 #[{ "owner_wallet_address" : WalletAddr, "sold_at": DateTime, "price": UnsignedInt}, ...]
    tx_hash = StringField()
    auction = ListField(EmbeddedDocumentField(Auction))


class Collections(Document):
    title = StringField(max_length=200, min_length=1, unique=True)
    nft_ids = ListField(StringField())
    category = StringField(min_length=1)
    creator = StringField(min_length=1) #### wallet address
    floor_price = StringField(min_value=0)
    minted_at = StringField()
    extra = DictField(StringField(), default=dict)
    description = StringField()
    logo = ImageField()
    chain = SequenceField()
    banner_image = ImageField()
    logo_path = StringField()
    banner_image_path = StringField()       
    updated_at = DateTimeField()
    created_at = DateTimeField()
    nft_owners_count = IntField(min_value=0)
    views = IntField(min_value=0)
    likes = ListField(StringField())


class Gencollections(Document):        #Generative Collection
    title = StringField(max_length=200, min_length=1, unique=True)
    nft_ids = ListField(StringField())
    category = StringField(min_length=1)
    creator = StringField(min_length=1)              #walletaddr
    minted_at = StringField()
    extra = DictField(StringField(), default=dict)
    updated_at = DateTimeField()
    description = StringField()
    logo = ImageField()
    chain = SequenceField()
    banner_image = ImageField()
    have_shop = BooleanField(default=False)
    logo_path = StringField()
    banner_image_path = StringField()       
    reveal = ListField(EmbeddedDocumentField(Reveal))
    created_at = DateTimeField()
    nft_mint = ListField(EmbeddedDocumentField(Nft_mint))
    metadata = FileField()
    metadata_save_path = StringField()
    nft_owners_count = IntField(min_value=0)
    views = IntField(min_value=0)
    likes = ListField(StringField())
    default_perpetual_royalties = ListField(EmbeddedDocumentField(Perpetual_royalties))
    mint_per_wallet = ListField(EmbeddedDocumentField(Mint_per_wallet))



class Basket(Document):
    nfts =  ListField(EmbeddedDocumentField(Basket_NFT_Info))
    buyer_info = EmbeddedDocumentField(Basket_Buyer_Info)
    total_price = StringField()
    tx_hash = StringField()
    purchased_at = StringField()