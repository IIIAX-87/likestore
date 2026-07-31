from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_sku', 'price', 'total']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'comment', 'created_by', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'status', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'delivery_type', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'id']
    readonly_fields = ['subtotal', 'delivery_cost', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    actions = ['confirm_orders', 'ship_orders']

    def confirm_orders(self, request, queryset):
        for order in queryset.filter(status='pending'):
            order.status = 'confirmed'
            order.confirmed_at = timezone.now()
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status='confirmed',
                comment='Заказ подтверждён',
                created_by=request.user,
            )
    confirm_orders.short_description = 'Подтвердить выбранные заказы'

    def ship_orders(self, request, queryset):
        for order in queryset.filter(status='confirmed'):
            order.status = 'shipped'
            order.shipped_at = timezone.now()
            order.save()
            OrderStatusHistory.objects.create(
                order=order,
                status='shipped',
                comment='Заказ отправлен',
                created_by=request.user,
            )
    ship_orders.short_description = 'Отправить выбранные заказы'


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_by', 'created_at']
    list_filter = ['status']


from django.utils import timezone
