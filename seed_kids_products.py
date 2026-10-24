"""
Seed Shankh Kids Products for ShopCRM / E-Commerce Storefront
Adds realistic kids-focused inventory products under the 'Shankh' brand.
"""
import os
import sys
from pathlib import Path
from decimal import Decimal

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

from ecommerce.models import Category, Product


def seed_kids_products():
    print("Seeding Shankh Kids inventory products...")

    kids_categories = [
        "Shankh Kids Dental Care",
        "Shankh Kids Nutrition & Gummies",
        "Shankh Kids Bath & Body",
        "Shankh Baby Essentials"
    ]
    cats = {}
    for cname in kids_categories:
        c, _ = Category.objects.get_or_create(name=cname)
        cats[cname] = c
    print(f"[OK] {len(cats)} Shankh Kids categories ready.")

    kids_products_data = [
        {
            'name': 'Shankh Kids Strawberry Toothpaste (Fluoride-Free, 80g)',
            'sku': 'SH-KID-101',
            'category': cats['Shankh Kids Dental Care'],
            'price': Decimal('199.00'),
            'cost_price': Decimal('85.00'),
            'stock_quantity': 50,
            'low_stock_threshold': 10,
            'image': 'products/1.png',
            'description': 'Safe-to-swallow natural strawberry flavored oral care paste designed specifically for young teeth and gums.'
        },
        {
            'name': 'Shankh Kids Ultra-Soft Animal Toothbrush (Pack of 2)',
            'sku': 'SH-KID-102',
            'category': cats['Shankh Kids Dental Care'],
            'price': Decimal('149.00'),
            'cost_price': Decimal('55.00'),
            'stock_quantity': 75,
            'low_stock_threshold': 15,
            'image': 'products/2.png',
            'description': 'Extra soft micro-bristles with animal suction-cup stand for safe, exciting daily brushing.'
        },
        {
            'name': 'Shankh Kids Super-Immunity Vitamin C & Zinc Gummies (60ct)',
            'sku': 'SH-KID-201',
            'category': cats['Shankh Kids Nutrition & Gummies'],
            'price': Decimal('499.00'),
            'cost_price': Decimal('220.00'),
            'stock_quantity': 40,
            'low_stock_threshold': 8,
            'image': 'products/3.png',
            'description': 'Pectin-based delicious mango gummies with organic Vitamin C, Zinc, and Elderberry for growing kids.'
        },
        {
            'name': 'Shankh Kids Brahmi Brain & Memory Herbal Syrup (200ml)',
            'sku': 'SH-KID-202',
            'category': cats['Shankh Kids Nutrition & Gummies'],
            'price': Decimal('299.00'),
            'cost_price': Decimal('130.00'),
            'stock_quantity': 5,  # Low stock demo!
            'low_stock_threshold': 10,
            'image': 'products/4.png',
            'description': 'Traditional Shankhpushpi and Brahmi herbal formulation to boost focus, cognitive stamina, and memory.'
        },
        {
            'name': 'Shankh Kids Tear-Free Gentle Shampoo & Body Wash (300ml)',
            'sku': 'SH-KID-301',
            'category': cats['Shankh Kids Bath & Body'],
            'price': Decimal('280.00'),
            'cost_price': Decimal('115.00'),
            'stock_quantity': 60,
            'low_stock_threshold': 12,
            'image': 'products/5.png',
            'description': 'Tear-free hypoallergenic wash with organic chamomile and aloe vera extract.'
        },
        {
            'name': 'Shankh Kids Fun Foaming Bubble Bath (Green Apple, 400ml)',
            'sku': 'SH-KID-302',
            'category': cats['Shankh Kids Bath & Body'],
            'price': Decimal('320.00'),
            'cost_price': Decimal('140.00'),
            'stock_quantity': 0,  # Out of stock demo!
            'low_stock_threshold': 10,
            'image': 'products/6.png',
            'description': 'Gentle sulfate-free bubble bath with fresh apple essence, leaving kids fresh and relaxed.'
        },
        {
            'name': 'Shankh Baby & Kids Nourishing Moisture Lotion (200ml)',
            'sku': 'SH-KID-401',
            'category': cats['Shankh Baby Essentials'],
            'price': Decimal('250.00'),
            'cost_price': Decimal('100.00'),
            'stock_quantity': 35,
            'low_stock_threshold': 8,
            'image': 'products/7.png',
            'description': 'Enriched with organic shea butter and sweet almond oil for 24-hour delicate skin protection.'
        },
        {
            'name': 'Shankh Kids Natural Mosquito Repellent Roll-On (50ml)',
            'sku': 'SH-KID-402',
            'category': cats['Shankh Baby Essentials'],
            'price': Decimal('160.00'),
            'cost_price': Decimal('60.00'),
            'stock_quantity': 80,
            'low_stock_threshold': 20,
            'image': 'products/8.png',
            'description': '100% natural outdoor protection roll-on with citronella and eucalyptus oils.'
        },
        {
            'name': 'Shankh Baby Organic Pure Water Wipes (Pack of 72)',
            'sku': 'SH-KID-403',
            'category': cats['Shankh Baby Essentials'],
            'price': Decimal('180.00'),
            'cost_price': Decimal('70.00'),
            'stock_quantity': 4,  # Low stock demo!
            'low_stock_threshold': 10,
            'image': 'products/9.png',
            'description': 'Biodegradable bamboo wipes made with 99% pure water and organic aloe vera.'
        }
    ]

    count = 0
    for pdata in kids_products_data:
        prod, created = Product.objects.get_or_create(sku=pdata['sku'], defaults={
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
        if not created:
            prod.name = pdata['name']
            prod.category = pdata['category']
            prod.price = pdata['price']
            prod.cost_price = pdata['cost_price']
            prod.stock_quantity = pdata['stock_quantity']
            prod.low_stock_threshold = pdata['low_stock_threshold']
            prod.stock = (pdata['stock_quantity'] > 0)
            prod.image = pdata['image']
            prod.description = pdata['description']
            prod.save()
        count += 1

    print(f"[OK] {count} Shankh Kids products successfully updated in database!")


if __name__ == '__main__':
    seed_kids_products()
