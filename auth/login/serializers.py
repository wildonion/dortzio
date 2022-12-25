



from rest_framework_mongoengine import serializers
from .models import Offers, Users







##### -------------------------
#####     Offers Serializer
##### -------------------------
class OffersSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Offers
        fields = '__all__'
        
        
        


##### -------------------------
#####      Users Serializer
##### -------------------------
class UsersSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Offers
        fields = '__all__'