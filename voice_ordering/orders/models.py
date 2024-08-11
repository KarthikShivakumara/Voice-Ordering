from django.db import models

class Order(models.Model):
    customer_name = models.CharField(max_length=100)
    seat_number = models.IntegerField()
    items = models.TextField()
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer_name} (Seat {self.seat_number})"
