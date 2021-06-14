from django.shortcuts import render
from gapi.serializers import ItemSerializer
from gapi.models import Items
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView

########################
# get all from database

class GetAllItems(ListAPIView):
   queryset = Items.objects.all()
   serializer_class = ItemSerializer
   pagination_class = PageNumberPagination

########################
# find title
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_title(request, title):
    
    if len(title) >= 3:
        items = Items.objects.filter(title__contains=title)
        serializer = ItemSerializer(items, many=True)

        if serializer.data:
            return Response(serializer.data)
        else:
            return Response(f'Nothing found for title[{title}]!')
    else:
        return Response( f"Error: 'title[{title}] must be at least three symbols!" );


########################
# get product_number
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_details(request, product_n):

    try:
        items = Items.objects.get(product_number=product_n)
    except Items.DoesNotExist as err:
        return Response(f'{err}.Searched product_number[{product_n}]')

    serializer = ItemSerializer(items)
    return Response(serializer.data)
