from django.contrib import admin
from .models import Order
import json
import os

@admin.action(description='Confirm selected orders')
def confirm_orders(modeladmin, request, queryset):
    orders_dir = os.path.join(os.path.dirname(__file__), 'order_files')
    for order in queryset:
        order.confirmed = True
        order.save()

        # Update the JSON file
        order_file = os.path.join(orders_dir, f"order_{order.id}.json")
        if os.path.exists(order_file):
            with open(order_file, 'r') as file:
                order_data = json.load(file)
            order_data['message'] = "Order confirmed!"
            with open(order_file, 'w') as file:
                json.dump(order_data, file)
        
    # Delete old files if there are more than six
    order_files = [f for f in os.listdir(orders_dir) if f.endswith('.json')]
    if len(order_files) > 6:
        order_files.sort(key=lambda f: os.path.getmtime(os.path.join(orders_dir, f)))
        for f in order_files[:-6]:
            os.remove(os.path.join(orders_dir, f))

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'seat_number', 'items', 'confirmed')
    actions = [confirm_orders]

admin.site.register(Order, OrderAdmin)