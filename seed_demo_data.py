"""
ShopCRM & Inventory Management - Demo Data Seeder
Populates a fresh SQLite database with realistic shop inventory,
customer profiles, orders, categories, coupons, and currencies.
"""
import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import timedelta

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeoayurcart.settings')
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import django
django.setup()

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import timezone
from ecommerce.models import (
    Category as ShopCategory, Product, ProductImage, Currency,
    Order, OrderProduct, Address, Coupon, UserProfile
)
from blog.models import Category as BlogCategory, Blog_Post, Team, Hashtags


def seed_database():
    print("Seeding ShopCRM & Inventory Management database...")

    # 1. Update Site
    site, _ = Site.objects.get_or_create(id=1)
    site.domain = '127.0.0.1:8000'
    site.name = 'ShopCRM Retail & Inventory Store'
    site.save()
    print("✔ Site configuration updated.")

    # 2. Create Superuser / Shop Admin
    admin_user, created = User.objects.get_or_create(username='admin')
    admin_user.set_password('admin123')
    admin_user.email = 'admin@shopcrm.local'
    admin_user.first_name = 'Shop'
    admin_user.last_name = 'Manager'
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print(f"✔ Admin account ready -> Username: admin | Password: admin123")

    # 3. Currencies
    currencies_data = [
        ('INR', 'Indian Rupee', '₹', Decimal('1.00')),
        ('USD', 'US Dollar', '$', Decimal('0.012')),
        ('EUR', 'Euro', '€', Decimal('0.011')),
    ]
    for code, name, symbol, rate in currencies_data:
        curr, _ = Currency.objects.get_or_create(
            code=code,
            defaults={'name': name, 'symbol': symbol, 'conversion_rate': rate}
        )
        curr.name = name
        curr.symbol = symbol
        curr.conversion_rate = rate
        curr.save()
    print(f"✔ {len(currencies_data)} currencies created.")

    # 4. Shop Categories
    shop_cats = [
        "Oral & Dental Care",
        "Ayurvedic & Herbal Wellness",
        "Personal Hygiene & Sanitization",
        "Skincare & Derma Essentials",
        "Daily Health Supplements"
    ]
    cat_objs = {}
    for cat_name in shop_cats:
        c, _ = ShopCategory.objects.get_or_create(name=cat_name)
        cat_objs[cat_name] = c
    print(f"✔ {len(cat_objs)} shop categories created.")

    # 5. Products with Inventory & SKU tracking
    products_data = [
        {
            'name': 'Microwhite Advanced Teeth Whitening Kit',
            'sku': 'MW-TW-001',
            'category': cat_objs['Oral & Dental Care'],
            'price': Decimal('499.00'),
            'cost_price': Decimal('210.00'),
            'stock_quantity': 45,
            'low_stock_threshold': 10,
            'image': 'products/1.png',
            'description': 'Clinically tested advanced enamel-safe teeth whitening kit with LED activator.'
        },
        {
            'name': 'Microwhite Activated Charcoal Toothpaste',
            'sku': 'MW-CT-002',
            'category': cat_objs['Oral & Dental Care'],
            'price': Decimal('249.00'),
            'cost_price': Decimal('110.00'),
            'stock_quantity': 75,
            'low_stock_threshold': 15,
            'image': 'products/2.png',
            'description': 'Natural activated organic charcoal toothpaste for stain removal and fresh breath.'
        },
        {
            'name': 'AyurHerb Pure Ashwagandha Vitality Capsules (60ct)',
            'sku': 'AH-ASH-101',
            'category': cat_objs['Ayurvedic & Herbal Wellness'],
            'price': Decimal('650.00'),
            'cost_price': Decimal('320.00'),
            'stock_quantity': 30,
            'low_stock_threshold': 8,
            'image': 'products/3.png',
            'description': 'Pure organic KSM-66 Ashwagandha root extract for stress relief and vitality.'
        },
        {
            'name': 'Organic Triphala Digestive Care Powder (200g)',
            'sku': 'AH-TRI-102',
            'category': cat_objs['Ayurvedic & Herbal Wellness'],
            'price': Decimal('320.00'),
            'cost_price': Decimal('140.00'),
            'stock_quantity': 4,  # LOW STOCK SAMPLE
            'low_stock_threshold': 10,
            'image': 'products/4.png',
            'description': 'Traditional ayurvedic trifala formula for gut health and gentle detoxification.'
        },
        {
            'name': 'Herbal Neem & Tulsi Purifying Hand Wash (500ml)',
            'sku': 'PH-HW-201',
            'category': cat_objs['Personal Hygiene & Sanitization'],
            'price': Decimal('180.00'),
            'cost_price': Decimal('75.00'),
            'stock_quantity': 85,
            'low_stock_threshold': 20,
            'image': 'products/5.png',
            'description': 'Antibacterial hand wash enriched with pure neem leaf and tulsi extract.'
        },
        {
            'name': 'Antiseptic Herbal Pocket Sanitizer Spray (100ml)',
            'sku': 'PH-SAN-202',
            'category': cat_objs['Personal Hygiene & Sanitization'],
            'price': Decimal('99.00'),
            'cost_price': Decimal('38.00'),
            'stock_quantity': 0,  # OUT OF STOCK SAMPLE
            'low_stock_threshold': 15,
            'image': 'products/6.png',
            'description': 'Alcohol-based instant germ protection sanitizer infused with aloe vera.'
        },
        {
            'name': 'Ayurvedic Kumkumadi Radiance Face Oil (30ml)',
            'sku': 'SD-KUM-301',
            'category': cat_objs['Skincare & Derma Essentials'],
            'price': Decimal('899.00'),
            'cost_price': Decimal('420.00'),
            'stock_quantity': 25,
            'low_stock_threshold': 5,
            'image': 'products/7.png',
            'description': 'Authentic Kumkumadi Thailam infused with saffron for deep hydration and natural glow.'
        },
        {
            'name': 'Pure 99% Soothing Aloe Vera Gel (250g)',
            'sku': 'SD-ALO-302',
            'category': cat_objs['Skincare & Derma Essentials'],
            'price': Decimal('220.00'),
            'cost_price': Decimal('90.00'),
            'stock_quantity': 50,
            'low_stock_threshold': 10,
            'image': 'products/8.png',
            'description': 'Cold-pressed natural aloe vera gel for soothing sun irritation and daily hydration.'
        },
        {
            'name': 'Immunity Gold Chyawanprash Special Blend (500g)',
            'sku': 'HS-CHY-401',
            'category': cat_objs['Daily Health Supplements'],
            'price': Decimal('550.00'),
            'cost_price': Decimal('260.00'),
            'stock_quantity': 3,  # LOW STOCK SAMPLE
            'low_stock_threshold': 8,
            'image': 'products/9.png',
            'description': 'Herbal formulation enriched with amla, saffron, and 40+ rejuvenating herbs.'
        },
        {
            'name': 'Organic Giloy & Tulsi Immunity Booster Drops (30ml)',
            'sku': 'HS-GIL-402',
            'category': cat_objs['Daily Health Supplements'],
            'price': Decimal('190.00'),
            'cost_price': Decimal('75.00'),
            'stock_quantity': 40,
            'low_stock_threshold': 10,
            'image': 'products/10.png',
            'description': 'Concentrated herbal extract drops supporting daily natural immunity.'
        }
    ]

    prod_objs = []
    for pdata in products_data:
        p, _ = Product.objects.get_or_create(sku=pdata['sku'], defaults={
            'name': pdata['name'],
            'category': pdata['category'],
            'price': pdata['price'],
            'cost_price': pdata['cost_price'],
            'stock_quantity': pdata['stock_quantity'],
            'low_stock_threshold': pdata['low_stock_threshold'],
            'stock': (pdata['stock_quantity'] > 0),
            'image': pdata['image'],
            'description': pdata['description'],
        })
        prod_objs.append(p)
    print(f"✔ {len(prod_objs)} inventory products registered with SKUs and stock counts.")

    # 6. Sample CRM Customer Accounts
    customers_data = [
        {
            'username': 'rohit.sharma',
            'name': 'Rohit Sharma',
            'email': 'rohit.sharma@example.com',
            'phone': '9876543210',
            'address': '42 MG Road, Indiranagar, Bangalore, Karnataka - 560038',
            'notes': 'Loyal customer. Prefers dental kits and weekend deliveries.',
            'loyalty': 140
        },
        {
            'username': 'priya.patel',
            'name': 'Priya Patel',
            'email': 'priya.patel@example.com',
            'phone': '9822334455',
            'address': '18 Park Avenue, Bandra West, Mumbai, Maharashtra - 400050',
            'notes': 'Interested in organic skincare and herbal supplements.',
            'loyalty': 95
        },
        {
            'username': 'amit.verma',
            'name': 'Dr. Amit Verma',
            'email': 'amit.verma@example.com',
            'phone': '9811223344',
            'address': '102 Sector 14, DLF Phase 2, Gurgaon, Haryana - 122002',
            'notes': 'Purchases dental & hygiene inventory in bulk for clinic.',
            'loyalty': 280
        }
    ]

    customer_objs = []
    for cdata in customers_data:
        user, ucreated = User.objects.get_or_create(username=cdata['username'])
        user.email = cdata['email']
        parts = cdata['name'].split()
        user.first_name = parts[0]
        user.last_name = parts[-1] if len(parts) > 1 else ''
        user.set_password('demo123')
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.name = cdata['name']
        profile.phone_number = cdata['phone']
        profile.address = cdata['address']
        profile.customer_notes = cdata['notes']
        profile.loyalty_points = cdata['loyalty']
        profile.save()

        # Add customer default address
        addr, _ = Address.objects.get_or_create(
            user=user,
            default=True,
            defaults={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': cdata['phone'],
                'address_line_1': cdata['address'].split(',')[0],
                'city': 'Bangalore' if 'Bangalore' in cdata['address'] else ('Mumbai' if 'Mumbai' in cdata['address'] else 'Gurgaon'),
                'state': 'Karnataka' if 'Karnataka' in cdata['address'] else ('Maharashtra' if 'Maharashtra' in cdata['address'] else 'Haryana'),
                'country': 'IN',
                'zipcode': '560038'
            }
        )
        customer_objs.append((user, addr))
    print(f"✔ {len(customer_objs)} CRM customer accounts created with profiles and addresses.")

    # 7. Sample Orders for CRM Dashboard
    orders_data = [
        {
            'customer_idx': 0,
            'status': 'delivered',
            'payment_status': 'paid',
            'payment_method': 'Cash on Delivery (Verified)',
            'days_ago': 5,
            'items': [(prod_objs[0], 1), (prod_objs[1], 2)]
        },
        {
            'customer_idx': 1,
            'status': 'shipped',
            'payment_status': 'paid',
            'payment_method': 'Online Payment (Demo Gateway)',
            'days_ago': 2,
            'items': [(prod_objs[2], 1), (prod_objs[6], 1)]
        },
        {
            'customer_idx': 2,
            'status': 'processing',
            'payment_status': 'unpaid',
            'payment_method': 'In-Store / Direct Invoice',
            'days_ago': 0,
            'items': [(prod_objs[4], 3), (prod_objs[7], 2)]
        }
    ]

    for odata in orders_data:
        cust_user, cust_addr = customer_objs[odata['customer_idx']]
        total_p = sum(prod.price * qty for prod, qty in odata['items'])
        order = Order.objects.create(
            user=cust_user,
            shipping_address=cust_addr,
            total_price=total_p,
            status=odata['status'],
            payment_status=odata['payment_status'],
            payment_method=odata['payment_method'],
        )
        for prod, qty in odata['items']:
            OrderProduct.objects.create(order=order, product=prod, quantity=qty)
    print(f"✔ {len(orders_data)} sample CRM orders generated with invoice line items.")

    # 8. Promotional Coupons
    now = timezone.now()
    coupons = [
        ('WELCOME10', Decimal('100.00'), Decimal('499.00'), now, now + timedelta(days=90)),
        ('SHOP50', Decimal('50.00'), Decimal('299.00'), now, now + timedelta(days=60)),
        ('FESTIVE200', Decimal('200.00'), Decimal('999.00'), now, now + timedelta(days=120)),
    ]
    for code, disc, min_p, start, end in coupons:
        c, _ = Coupon.objects.get_or_create(code=code, defaults={
            'discount_amount': disc,
            'min_purchase_amount': min_p,
            'start_date': start,
            'end_date': end,
            'is_active': True
        })
    print(f"✔ {len(coupons)} promotional coupons created.")

    # 9. Blog demo posts & Author Team
    team_member, _ = Team.objects.get_or_create(name='Dr. Neha Kulkarni', defaults={
        'position': 'Chief Wellness Consultant & Product Formulator',
        'description': 'Ayurvedic practitioner and certified health specialist with 12+ years experience in natural care.'
    })
    blog_cat, _ = BlogCategory.objects.get_or_create(title='Dental Care')
    blog_cat2, _ = BlogCategory.objects.get_or_create(title='Ayurvedic Health')

    sample_post, pcreated = Blog_Post.objects.get_or_create(
        title='5 Natural Ingredients for Healthier Teeth & Gums',
        defaults={
            'author': team_member,
            'Description': '<p>Maintaining optimal oral hygiene goes beyond daily brushing. In this guide, we explore the science-backed benefits of charcoal, neem, clove, and herbal mouth rinses.</p>',
            'meta_title': 'Natural Oral Hygiene Guide',
            'meta_description': 'Discover top natural ingredients for daily dental care.',
            'thumbnail_800_563': 'new_media/1.jpg'
        }
    )
    sample_post.thumbnail_800_563 = 'new_media/1.jpg'
    sample_post.save()
    sample_post.categories.add(blog_cat)

    sample_post2, _ = Blog_Post.objects.get_or_create(
        title='How Daily Ashwagandha Helps Balance Stress and Energy',
        defaults={
            'author': team_member,
            'Description': '<p>Ashwagandha is one of the most revered adaptogens in traditional herbal medicine. Learn how regular supplementation supports restful sleep and sustained daily energy.</p>',
            'meta_title': 'Ashwagandha Benefits and Usage',
            'meta_description': 'Guide to adaptogenic herbs and vitality.',
            'thumbnail_800_563': 'new_media/2.jpg'
        }
    )
    sample_post2.thumbnail_800_563 = 'new_media/2.jpg'
    sample_post2.save()
    sample_post2.categories.add(blog_cat2)
    print("✔ Blog posts and team author profiles created.")

    print("\n==================================================================")
    print("DEMO DATA SEEDING COMPLETE!")
    print("Admin Portal:     http://127.0.0.1:8000/admin/")
    print("Credentials:      admin / admin123")
    print("Customer Portal:  http://127.0.0.1:8000/")
    print("Customer Logins:  rohit.sharma / demo123, priya.patel / demo123")
    print("==================================================================")


if __name__ == '__main__':
    seed_database()
