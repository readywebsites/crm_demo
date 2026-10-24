from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Category, Product, ProductImage, Currency, Order, OrderProduct,
    Address, Coupon, UserProfile
)


# ==============================================================================
# INVENTORY MANAGEMENT: Products & Stock
# ==============================================================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku_code',
        'category',
        'price_display',
        'cost_display',
        'stock_quantity',
        'inventory_status',
        'stock',
        'created_at'
    )
    list_filter = ('category', 'stock', 'created_at')
    search_fields = ('name', 'sku', 'description')
    list_editable = ('stock_quantity', 'stock')
    inlines = [ProductImageInline]
    actions = ['restock_25_units', 'restock_50_units', 'mark_in_stock', 'mark_out_of_stock']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'category', 'description', 'image')
        }),
        ('Pricing & Financials', {
            'fields': ('price', 'cost_price')
        }),
        ('Shop Inventory Controls', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'stock')
        }),
    )

    def sku_code(self, obj):
        return obj.sku or '-'
    sku_code.short_description = 'SKU / Barcode'

    def price_display(self, obj):
        return f"₹{obj.price}"
    price_display.short_description = 'Retail Price'

    def cost_display(self, obj):
        return f"₹{obj.cost_price}"
    cost_display.short_description = 'Cost Price'

    def inventory_status(self, obj):
        if obj.stock_quantity <= 0 or not obj.stock:
            return format_html('<span style="color: #d9534f; font-weight: bold; background: #fdf2f2; padding: 2px 8px; border-radius: 4px;">● Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html(
                '<span style="color: #f0ad4e; font-weight: bold; background: #fefcf2; padding: 2px 8px; border-radius: 4px;">⚠ Low Stock ({})</span>',
                obj.stock_quantity
            )
        else:
            return format_html(
                '<span style="color: #5cb85c; font-weight: bold; background: #f2fbf2; padding: 2px 8px; border-radius: 4px;">✔ In Stock ({})</span>',
                obj.stock_quantity
            )
    inventory_status.short_description = 'Inventory Health'

    # Admin actions for shopkeeper
    def restock_25_units(self, request, queryset):
        updated = 0
        for product in queryset:
            product.stock_quantity += 25
            product.stock = True
            product.save()
            updated += 1
        self.message_user(request, f"Successfully restocked 25 units for {updated} product(s).")
    restock_25_units.short_description = "📦 Restock (+25 units)"

    def restock_50_units(self, request, queryset):
        updated = 0
        for product in queryset:
            product.stock_quantity += 50
            product.stock = True
            product.save()
            updated += 1
        self.message_user(request, f"Successfully restocked 50 units for {updated} product(s).")
    restock_50_units.short_description = "📦 Restock (+50 units)"

    def mark_in_stock(self, request, queryset):
        queryset.update(stock=True)
        self.message_user(request, "Selected products marked as available in shop.")
    mark_in_stock.short_description = "✔ Mark as In Stock"

    def mark_out_of_stock(self, request, queryset):
        queryset.update(stock=False, stock_quantity=0)
        self.message_user(request, "Selected products marked as out of stock.")
    mark_out_of_stock.short_description = "✖ Mark as Out of Stock"


# ==============================================================================
# SALES & ORDER MANAGEMENT
# ==============================================================================

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('product', 'quantity', 'item_total')
    can_delete = False

    def item_total(self, obj):
        if obj.id:
            return f"₹{obj.product.price * obj.quantity}"
        return "-"
    item_total.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_id',
        'customer_display',
        'customer_phone',
        'total_amount',
        'payment_status_badge',
        'order_status_badge',
        'created_at'
    )
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'shipping_address__first_name', 'shipping_address__phone')
    inlines = [OrderProductInline]
    actions = ['mark_paid', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    def invoice_id(self, obj):
        return obj.get_invoice_number()
    invoice_id.short_description = 'Invoice #'

    def customer_display(self, obj):
        if obj.shipping_address:
            return f"{obj.shipping_address.first_name} {obj.shipping_address.last_name}"
        return obj.user.get_full_name() or obj.user.username
    customer_display.short_description = 'Customer'

    def customer_phone(self, obj):
        if obj.shipping_address and obj.shipping_address.phone:
            return obj.shipping_address.phone
        if hasattr(obj.user, 'userprofile') and obj.user.userprofile.phone_number:
            return obj.user.userprofile.phone_number
        return "-"
    customer_phone.short_description = 'Contact'

    def total_amount(self, obj):
        return f"₹{obj.total_price}"
    total_amount.short_description = 'Total Amount'

    def payment_status_badge(self, obj):
        colors = {
            'paid': '#5cb85c',
            'unpaid': '#f0ad4e',
            'failed': '#d9534f',
        }
        color = colors.get(obj.payment_status, '#777')
        return format_html(
            '<span style="color: {}; font-weight: bold; text-transform: uppercase;">● {}</span>',
            color, obj.payment_status
        )
    payment_status_badge.short_description = 'Payment Status'

    def order_status_badge(self, obj):
        colors = {
            'delivered': '#5cb85c',
            'shipped': '#0275d8',
            'processing': '#5bc0de',
            'pending': '#f0ad4e',
            'cancelled': '#d9534f',
        }
        color = colors.get(obj.status, '#777')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; text-transform: uppercase;">{}</span>',
            color, obj.status
        )
    order_status_badge.short_description = 'Fulfillment Status'

    # Order management actions
    def mark_paid(self, request, queryset):
        queryset.update(payment_status='paid')
        self.message_user(request, "Selected orders marked as Paid.")
    mark_paid.short_description = "💳 Mark as Paid"

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, "Selected orders marked as Processing.")
    mark_processing.short_description = "⚙ Mark as Processing"

    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, "Selected orders marked as Shipped.")
    mark_shipped.short_description = "🚚 Mark as Shipped"

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered', payment_status='paid')
        self.message_user(request, "Selected orders marked as Delivered.")
    mark_delivered.short_description = "✔ Mark as Delivered"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, "Selected orders marked as Cancelled.")
    mark_cancelled.short_description = "✖ Mark as Cancelled"


# ==============================================================================
# CRM: Customer Management & User Profiles
# ==============================================================================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Customer CRM Profile'
    fk_name = 'user'
    fields = ('name', 'phone_number', 'address', 'loyalty_points', 'customer_notes')


# Unregister default User admin and register customized CRM User admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomerCRMAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username',
        'customer_name',
        'email',
        'customer_phone',
        'loyalty_points_display',
        'orders_count',
        'is_staff'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__phone_number')

    def customer_name(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile.name:
            return obj.userprofile.name
        return f"{obj.first_name} {obj.last_name}".strip() or "-"
    customer_name.short_description = 'Full Name'

    def customer_phone(self, obj):
        return obj.userprofile.phone_number if hasattr(obj, 'userprofile') else '-'
    customer_phone.short_description = 'Phone'

    def loyalty_points_display(self, obj):
        if hasattr(obj, 'userprofile'):
            return f"⭐ {obj.userprofile.loyalty_points}"
        return "-"
    loyalty_points_display.short_description = 'Loyalty Pts'

    def orders_count(self, obj):
        count = Order.objects.filter(user=obj).count()
        return format_html('<b>{} orders</b>', count)
    orders_count.short_description = 'Order History'


# ==============================================================================
# OTHER MODELS: Categories, Addresses, Coupons, Currencies
# ==============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products in Category'


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'min_purchase_amount', 'start_date', 'end_date', 'is_active')
    search_fields = ('code',)
    list_filter = ('is_active', 'start_date', 'end_date')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'state', 'phone', 'default')
    search_fields = ('first_name', 'last_name', 'city', 'phone')
    list_filter = ('default', 'state', 'country')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'conversion_rate')
    search_fields = ('code', 'name')
