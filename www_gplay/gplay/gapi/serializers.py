from rest_framework import serializers

from gapi.models import Items

class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
       model = Items
       fields = ['product_number', 'category' ,'subcategory' ,'title' , 'subtitle', 'price', 'source_url']
       many=True 
