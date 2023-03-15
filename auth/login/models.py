


from mongoengine import *
import os



##### -------------------------
#####       Offers Model
##### -------------------------
class Offers(EmbeddedDocument):
    status_choise = (('accepted', 'Accepted'), ('waiting', 'Waiting'), ('cenceled', 'Canceled'))
    nft_id = StringField()
    nft_title = StringField()
    nft_media = StringField()
    from_wallet_address = StringField()
    to_wallet_address = StringField()
    price = StringField()
    expiration = StringField()
    date = StringField()
    is_active = BooleanField(default=True)
    status = StringField(choices=status_choise)
    


##### -------------------------
#####       Users Model
##### -------------------------
class Users(Document):
    username = StringField(min_length=1, max_length=200)
    user_id = StringField(max_length=200)
    reg_date = DateTimeField()
    avatar = ImageField()
    banner = ImageField()
    last_connect = DateTimeField()
    description = StringField(max_length=300)
    avatar_path = StringField()
    banner_path = StringField()
    offers = ListField(EmbeddedDocumentField(Offers)) 
    extra = DictField(StringField(), default=dict)