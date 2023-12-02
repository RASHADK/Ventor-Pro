from django.db import models
from django.utils import timezone

# Create your models here.

class Vendor(models.Model):
    name = models.CharField(max_length=200)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=20,unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return self.name 

    def update_historical_performance(self):
        HistoricalPerformance.objects.create(
            Vendor=self,
            date=timezone.now(),
            on_time_delivery_rate=self.on_time_delivery_rate,
            quality_rating_avg=self.quality_rating_avg,
            average_response_time=self.average_response_time,
            fulfillment_rate=self.fulfillment_rate,
        )  
    
    def update_on_time_delivery_rate(self):
        completed_orders = self.purchaseorder_set.filter(status='completed')
        total_completed_orders = completed_orders.count()
        on_time_deliveries = completed_orders.filter(delivery_date__lte=timezone.now()).count()

        if total_completed_orders > 0:
            self.on_time_delivery_rate = (on_time_deliveries / total_completed_orders) * 100
        else:
            self.on_time_delivery_rate = 0

        self.save()

    def update_quality_rating_average(self):
        completed_orders_with_rating = self.purchaseorder_set.filter(status='completed', quality_rating__isnull=False)
        total_completed_orders_with_rating = completed_orders_with_rating.count()
        total_quality_ratings = completed_orders_with_rating.aggregate(models.Sum('quality_rating'))['quality_rating__sum']

        if total_completed_orders_with_rating > 0:
            self.quality_rating_avg = total_quality_ratings / total_completed_orders_with_rating
        else:
            self.quality_rating_avg = 0

        self.save()

    def update_average_response_time(self):
        acknowledged_orders = self.purchaseorder_set.filter(acknowledgment_date__isnull=False)
        total_acknowledged_orders = acknowledged_orders.count()
        total_response_time = sum((order.acknowledgment_date - order.issue_date).total_seconds() for order in acknowledged_orders)

        if total_acknowledged_orders > 0:
            self.average_response_time = total_response_time / total_acknowledged_orders
        else:
            self.average_response_time = 0

        self.save()

    def update_fulfillment_rate(self):
        completed_orders = self.purchaseorder_set.filter(status='completed')
        total_completed_orders = completed_orders.count()
        fulfilled_orders = completed_orders.exclude(quality_rating__lt=1)  # Assuming quality_rating less than 1 indicates issues

        if total_completed_orders > 0:
            self.fulfillment_rate = (fulfilled_orders.count() / total_completed_orders) * 100
        else:
            self.fulfillment_rate = 0

        self.save()
class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True) 
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')    
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.po_number
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.status == 'completed':
            # Update Vendor's on-time delivery rate when a purchase order is completed
            self.vendor.update_on_time_delivery_rate()

            # Update Vendor's quality rating average when a quality rating is provided
            if self.quality_rating is not None:
                self.vendor.update_quality_rating_average()

            # Update Vendor's fulfillment rate when a purchase order is completed without issues
            self.vendor.update_fulfillment_rate()

    def acknowledge(self):
        # Logic for acknowledging a purchase order
        # ...

        # Update Vendor's average response time when a purchase order is acknowledged
        self.vendor.update_average_response_time()

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"    