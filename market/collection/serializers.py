



from rest_framework_mongoengine import serializers
from .models import NFTs, Collections







##### -------------------------
#####     Owners Serializer
##### -------------------------
class NFTsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = NFTs
        fields = '__all__'
        
        
        


##### -------------------------
#####   Collections Serializer
##### -------------------------
class CollectionsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Collections
        fields = '__all__'