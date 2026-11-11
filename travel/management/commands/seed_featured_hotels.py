from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from travel.models import Destination, Hotel


class Command(BaseCommand):
    help = "Create or update the three featured KhmerGlobe hotel listings."

    def handle(self, *args, **options):
        siem_reap, _ = Destination.objects.update_or_create(
            slug="siem-reap",
            defaults={
                "name": "Siem Reap",
                "country": "Cambodia",
                "summary": "Gateway to Angkor Wat and Cambodia's heritage.",
                "description": (
                    "Explore the temples of Angkor, Khmer culture, local markets "
                    "and the hospitality of Siem Reap."
                ),
                "is_featured": True,
                "is_active": True,
            },
        )

        phnom_penh, _ = Destination.objects.update_or_create(
            slug="phnom-penh",
            defaults={
                "name": "Phnom Penh",
                "country": "Cambodia",
                "summary": "Cambodia's capital, riverside and cultural centre.",
                "description": (
                    "Discover the Royal Palace, National Museum, riverside, "
                    "restaurants and the modern capital of Cambodia."
                ),
                "is_featured": True,
                "is_active": True,
            },
        )

        hotels = [
            {
                "destination": siem_reap,
                "name": "Sokha Angkor Resort",
                "slug": "sokha-angkor-resort",
                "category": 5,
                # Zero is deliberate: enter a verified quote before accepting bookings.
                "price_per_night": Decimal("0.00"),
                "summary": (
                    "Five-star Khmer-inspired resort in central Siem Reap, "
                    "near the Old Market and Angkor attractions."
                ),
                "description": (
                    "Sokha Angkor Resort offers Khmer-inspired rooms and suites "
                    "in the heart of Siem Reap. The resort is a convenient base "
                    "for visiting Angkor Wat, the Old Market and Pub Street. "
                    "Guests can enjoy dining outlets, a salt-water swimming "
                    "pool, Jasmine Spa, fitness facilities and meeting spaces. "
                    "Room categories and facilities are subject to the hotel's "
                    "current offering."
                ),
                "amenities": "\n".join([
                    "Complimentary Wi-Fi",
                    "Salt-water swimming pool",
                    "Jasmine Spa",
                    "Fitness centre",
                    "Steam, sauna and jacuzzi",
                    "Restaurants and bar",
                    "Meeting and conference facilities",
                    "Concierge and airport transfer arrangements",
                ]),
                "room_details": (
                    "Room categories include Deluxe City View, Deluxe Pool View "
                    "and suites. Room sizes, bedding, occupancy and inclusions "
                    "vary by category; confirm directly with the hotel."
                ),
                "image_url": "",
                "website_url": "https://www.sokhahotels.com.kh/angkor/",
                "price_note": (
                    "Contact the hotel or KhmerGlobe for a date-specific quote. "
                    "No live rate is configured; taxes and availability must be confirmed."
                ),
                "is_active": True,
            },
            {
                "destination": phnom_penh,
                "name": "Hyatt Regency Phnom Penh",
                "slug": "hyatt-regency-phnom-penh",
                "category": 5,
                "price_per_night": Decimal("0.00"),
                "summary": (
                    "Luxury five-star hotel in central Phnom Penh, close to "
                    "the Royal Palace and National Museum."
                ),
                "description": (
                    "Hyatt Regency Phnom Penh is located at #55, Street 178, "
                    "in the heart of the capital. The hotel offers 247 rooms "
                    "and suites, several dining experiences, meeting spaces, "
                    "a fitness centre, an outdoor pool, spa services and "
                    "concierge support. Room rates and availability depend "
                    "on dates and room category."
                ),
                "amenities": "\n".join([
                    "Complimentary internet access",
                    "Outdoor swimming pool",
                    "Fitness centre",
                    "Spa",
                    "Restaurants and room service",
                    "Meeting and event facilities",
                    "Concierge",
                    "Parking",
                    "Laundry service",
                ]),
                "room_details": (
                    "Room categories include King and Twin rooms, Palace View "
                    "rooms, Deluxe rooms and suites. The official rooms page "
                    "lists room sizes and category-specific features; confirm "
                    "the selected room and occupancy before booking."
                ),
                "image_url": "",
                "website_url": (
                    "https://www.hyatt.com/hyatt-regency/en-US/"
                    "pnhrp-hyatt-regency-phnom-penh"
                ),
                "price_note": (
                    "Contact the hotel or KhmerGlobe for a date-specific quote. "
                    "No live rate is configured; taxes and availability must be confirmed."
                ),
                "is_active": True,
            },
            {
                "destination": phnom_penh,
                "name": "NagaWorld",
                "slug": "nagaworld-phnom-penh",
                "category": 5,
                "price_per_night": Decimal("0.00"),
                "summary": (
                    "Five-star integrated resort in Phnom Penh with two hotel "
                    "towers, dining and entertainment facilities."
                ),
                "description": (
                    "NagaWorld is an integrated resort in central Phnom Penh. "
                    "Its accommodation is provided across NagaWorld1 and "
                    "NagaWorld2, with room and suite categories including "
                    "Superior, Deluxe and suite options. Selected rooms offer "
                    "Mekong River views. Guests can check the official website "
                    "for current room categories, facilities, restrictions "
                    "and booking conditions."
                ),
                "amenities": "\n".join([
                    "Complimentary in-room Wi-Fi",
                    "Flat-screen television",
                    "In-room electronic safe",
                    "Coffee and tea-making facilities",
                    "Mini-bar",
                    "Room service",
                    "Restaurants and bars",
                    "Spa and entertainment facilities",
                    "Shopping gallery",
                ]),
                "room_details": (
                    "Room types include Superior King, Superior Twin, Deluxe "
                    "King, Deluxe Twin and suite categories. Features vary by "
                    "room type; check the official room page for details."
                ),
                "image_url": "",
                "website_url": "https://www.nagaworld.com/",
                "price_note": (
                    "Contact the hotel or KhmerGlobe for a date-specific quote. "
                    "No live rate is configured; taxes and availability must be confirmed."
                ),
                "is_active": True,
            },
        ]

        for data in hotels:
            slug = data.pop("slug")
            hotel, created = Hotel.objects.update_or_create(
                slug=slug,
                defaults=data,
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {hotel.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                "Finished. Two destinations and three hotel listings are ready. "
                "Add verified prices and approved hotel images before accepting bookings."
            )
        )
