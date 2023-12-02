from django.shortcuts import render
from .models import Vendor,PurchaseOrder,HistoricalPerformance
from rest_framework import viewsets
from .serializer import VendorSerializer,PurchaseSerializer,HistoricalPerformanceSerializer
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class VendorView(viewsets.ViewSet):
    def list(self,request,*args,**kwargs):
        ven=Vendor.objects.all()
        ser=VendorSerializer(ven,many=True)
        return Response(data=ser.data)  
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=Vendor.objects.get(id=id)
        ser=VendorSerializer(item)
        return Response(data=ser.data)  
    def create(self,request,*args,**kwargs):
       ser=VendorSerializer(data=request.data)
       if ser.is_valid():
           ser.save()
           return Response({"msg":"Added"})
       else:
          return Response({"msg":ser.errors},status=status.HTTP_404_NOT_FOUND)
    def update(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=Vendor.objects.get(id=id)
        ser=VendorSerializer(data=request.data,instance=item)
        if ser.is_valid():
          ser.save()
          return Response({"msg":"Updated"})
        else:
            return Response({"msg":ser.errors},status=status.HTTP_404_NOT_FOUND)
    def destroy(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=Vendor.objects.get(id=id)
        item.delete()
        return Response({"msg":"Deleted"})   
    def performance(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance:
            performance_data = {
                'on_time_delivery_rate': instance.on_time_delivery_rate,
                'quality_rating_avg': instance.quality_rating_avg,
                'average_response_time': instance.average_response_time,
                'fulfillment_rate': instance.fulfillment_rate,
            }

            return Response(performance_data)
        else:
            return Response({'detail': 'Vendor not found.'}, status=404)
class PurchaseOrderView(viewsets.ViewSet):
    def list(self,request,*args,**kwargs):
        Item=PurchaseOrder.objects.all()
        ser=PurchaseSerializer(Item,many=True)
        return Response(data=ser.data) 
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=PurchaseOrder.objects.get(id=id)
        ser=PurchaseSerializer(item)
        return Response(data=ser.data)   
    def create(self,request,*args,**kwargs):
       ser=PurchaseSerializer(data=request.data)
       if ser.is_valid():
           ser.save()
           return Response({"msg":"Added"})
       else:
          return Response({"msg":ser.errors},status=status.HTTP_404_NOT_FOUND)
    def update(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=PurchaseOrder.objects.get(id=id)
        ser=PurchaseSerializer(data=request.data,instance=item)
        if ser.is_valid():
          ser.save()
          return Response({"msg":"Updated"})
        else:
            return Response({"msg":ser.errors},status=status.HTTP_404_NOT_FOUND)   
    def destroy(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=PurchaseOrder.objects.get(id=id)
        item.delete()
        return Response({"msg":"Deleted"})         
    def acknowledge(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Assuming acknowledgment_date is provided in the request data
        acknowledgment_date = request.data.get('acknowledgment_date')

        if acknowledgment_date:
            instance.acknowledgment_date = acknowledgment_date
            instance.save()

            # Trigger recalculation of average_response_time
            instance.vendor.update_performance_metrics()

            return Response({'detail': 'Acknowledgment successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Missing acknowledgment_date in request data.'}, status=status.HTTP_400_BAD_REQUEST)

class HistoricalPerformanceViewSet(viewsets.ViewSet):
    def list(self,request,*args,**kwargs):
        Item=HistoricalPerformance.objects.all()
        ser=HistoricalPerformanceSerializer(Item,many=True)
        return Response(data=ser.data) 
    def retrieve(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        item=HistoricalPerformance.objects.get(id=id)
        ser=HistoricalPerformanceSerializer(item)
        return Response(data=ser.data)