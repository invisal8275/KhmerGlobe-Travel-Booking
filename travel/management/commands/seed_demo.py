from decimal import Decimal
from django.core.management.base import BaseCommand
from travel.models import Destination, Tour, Hotel

class Command(BaseCommand):
    help = "Load KhmerGlobe presentation-ready destination, tour and hotel demo content."

    def handle(self, *args, **options):
        # Remove the original generic placeholder products from the first starter build.
        Tour.objects.filter(title__in=[
            "Classic Cambodia Discovery", "Phnom Penh & Island Escape",
            "Mekong Multi-Country Explorer", "Angkor Heritage Highlights",
        ]).delete()
        Hotel.objects.filter(name__startswith="Sample ").delete()

        destinations_data = [
            {
                "name": "Siem Reap", "country": "Cambodia",
                "summary": "Gateway to Angkor Wat, ancient Khmer temples and Tonlé Sap",
                "description": "Discover the former heart of the Khmer Empire. Siem Reap combines the monumental temples of Angkor, lively markets, traditional crafts, countryside villages and the Tonlé Sap lake region.",
                "image_url": "https://www.celebritycruises.com/blog/content/uploads/2020/05/celebrity-wonders-angkor-wat-siem-reap-cambodia.jpg",
            },
            {
                "name": "Phnom Penh", "country": "Cambodia",
                "summary": "Royal heritage, riverside life and modern Khmer culture",
                "description": "Cambodia's capital brings together the Royal Palace, Silver Pagoda, National Museum, lively riverfront and a dynamic food and arts scene.",
                "image_url": "/static/travel/images/destinations/phnom_penh.jpg",
            },
            {
                "name": "Koh Rong", "country": "Cambodia",
                "summary": "Tropical beaches, turquoise water and island escapes",
                "description": "Slow down on Cambodia's island coast with soft-sand beaches, clear water, boat trips, snorkeling and relaxed seaside stays.",
                "image_url": "/static/travel/images/destinations/koh_rong.jpg",
            },
            {
                "name": "Luang Prabang", "country": "Laos",
                "summary": "UNESCO-listed heritage, temples and waterfalls",
                "description": "A graceful Mekong town known for its Buddhist temples, traditional architecture, morning alms ceremony and nearby Kuang Si waterfalls.",
                "image_url": "/static/travel/images/destinations/luang_prabang.jpg",
            },
            {
                "name": "Hanoi", "country": "Vietnam",
                "summary": "Old Quarter lanes, lakeside landmarks and Vietnamese cuisine",
                "description": "Explore Hanoi's Old Quarter, Hoan Kiem Lake, historic temples, French-era architecture, street food and cultural performances.",
                "image_url": "/static/travel/images/destinations/hanoi.jpg",
            },
            {
                "name": "Singapore", "country": "Singapore",
                "summary": "A garden city of skyline icons, food and culture",
                "description": "Discover Marina Bay, Gardens by the Bay, vibrant neighbourhoods and world-class dining.",
                "image_url": "https://i.insider.com/5cfed1e24cf27011b74cf93a?auto=webp&format=jpeg&width=800",
            },
            {
                "name": "Dubai", "country": "United Arab Emirates",
                "summary": "Modern architecture, desert experiences and Arabian hospitality",
                "description": "Explore Dubai's beaches, iconic skyline, historic creek district and desert landscapes.",
                "image_url": "https://media.cntraveler.com/photos/563126d4c406c560343dfdeb/master/pass/burj-al-arab-dubai-cr-alamy.jpg",
            },
        ]
        destinations = {}
        for item in destinations_data:
            obj, _ = Destination.objects.update_or_create(
                name=item["name"],
                defaults={**item, "is_featured": True, "is_active": True},
            )
            destinations[item["name"]] = obj

        tours_data = [
            {
                "title": "Angkor Heritage & Sunrise Discovery",
                "destination": "Siem Reap", "days": 3, "kind": "basic",
                "price": "295.00",
                "summary": "A three-day introduction to Angkor Wat, Bayon and Ta Prohm.",
                "description": "Experience the essential Angkor temples with a local guide, time for sunrise photography and an introduction to Siem Reap's markets and Khmer cuisine. This compact journey is ideal for first-time visitors.",
                "itinerary": "DAY 1 — ARRIVAL IN SIEM REAP: Meet your driver, transfer to the hotel and enjoy a relaxed orientation walk around the Old Market and Pub Street area.\n\nDAY 2 — ANGKOR SUNRISE & SMALL CIRCUIT: Early departure for sunrise at Angkor Wat. Continue to Angkor Thom, Bayon and Ta Prohm with a licensed local guide. Return to town in the afternoon.\n\nDAY 3 — LOCAL CULTURE & DEPARTURE: Visit a local craft workshop or market, enjoy free time, then transfer to the airport.",
                "inclusions": "• 2 nights accommodation in a selected hotel\n• Daily breakfast\n• Private air-conditioned transfers as listed\n• English-speaking local guide on the Angkor touring day\n• Drinking water during touring\n• Itinerary planning and booking assistance",
                "exclusions": "• International and domestic flights\n• Angkor temple pass (payable separately at the official ticket office)\n• Lunches, dinners and personal expenses\n• Travel insurance, tips and optional activities",
                "image": "https://www.celebritycruises.com/blog/content/uploads/2020/05/celebrity-wonders-angkor-wat-siem-reap-cambodia.jpg",
            },
            {
                "title": "Classic Cambodia: Temples, Capital & Countryside",
                "destination": "Siem Reap", "days": 6, "kind": "private",
                "price": "695.00",
                "summary": "A balanced six-day journey from Angkor's temples to Phnom Penh.",
                "description": "Pair the majesty of Angkor with the character of Cambodia's capital. Discover ancient architecture, royal history, local food, countryside scenery and the rhythm of the Mekong region.",
                "itinerary": "DAY 1 — ARRIVE SIEM REAP: Airport greeting, hotel transfer and free evening.\n\nDAY 2 — ANGKOR WAT & ANGKOR THOM: Sunrise option, Angkor Wat, Bayon and the ancient royal city.\n\nDAY 3 — TA PROHM & BANTEAY SREI: Explore the atmospheric tree-root temple of Ta Prohm and the detailed pink sandstone carvings of Banteay Srei.\n\nDAY 4 — SIEM REAP TO PHNOM PENH: Travel by private vehicle or selected domestic connection; stop for local scenery en route when travelling by road.\n\nDAY 5 — PHNOM PENH CITY & ROYAL HERITAGE: Royal Palace area, National Museum and riverside. Tuol Sleng or other historical visits can be arranged according to guest preference.\n\nDAY 6 — DEPARTURE: Breakfast and transfer to the airport.",
                "inclusions": "• 5 nights accommodation in selected 3–4 star hotels\n• Daily breakfast\n• Private air-conditioned transfers between listed stops\n• English-speaking guide for scheduled sightseeing\n• Drinking water during touring\n• Basic itinerary coordination",
                "exclusions": "• Flights and visa fees\n• Angkor Pass and other attraction tickets unless specifically confirmed\n• Lunches, dinners, drinks and gratuities\n• Optional experiences and personal expenses",
                "image": "https://www.celebritycruises.com/blog/content/uploads/2020/05/celebrity-wonders-angkor-wat-siem-reap-cambodia.jpg",
            },
            {
                "title": "Cambodia Highlights: Heritage to the Coast",
                "destination": "Phnom Penh", "days": 8, "kind": "private",
                "price": "1090.00",
                "summary": "Eight days of Phnom Penh, Angkor heritage and a Koh Rong beach break.",
                "description": "A signature Cambodia itinerary that combines cultural landmarks with island downtime. Enjoy guided city visits, the temples of Angkor and a relaxing coastal finish.",
                "itinerary": "DAY 1 — ARRIVAL PHNOM PENH: Private arrival transfer and hotel check-in.\n\nDAY 2 — PHNOM PENH HERITAGE: Explore the Royal Palace precinct, National Museum and riverside district.\n\nDAY 3 — TRAVEL TO SIEM REAP: Transfer to Siem Reap and enjoy a relaxed evening.\n\nDAY 4 — ANGKOR WAT & ANGKOR THOM: Guided temple exploration with time for photography.\n\nDAY 5 — TA PROHM & LOCAL LIFE: Visit Ta Prohm and selected local craft or village experiences.\n\nDAY 6 — TRAVEL TO THE COAST: Transfer toward Sihanoukville and connect to Koh Rong by boat (subject to ferry schedule).\n\nDAY 7 — KOH RONG AT LEISURE: Beach time, swimming or optional snorkeling excursion.\n\nDAY 8 — DEPARTURE: Boat and road transfer for onward departure.",
                "inclusions": "• 7 nights accommodation in selected hotels/resort\n• Daily breakfast\n• Private ground transfers listed in the itinerary\n• Scheduled boat transfer to/from Koh Rong (subject to timetable)\n• Local English-speaking guides for city and temple touring\n• Drinking water during touring",
                "exclusions": "• International flights and visa\n• Angkor Pass, meals not stated and beverages\n• Optional boat trips, diving and water sports\n• Tips, insurance and personal expenses",
                "image": "/static/travel/images/destinations/koh_rong.jpg",
            },
            {
                "title": "Mekong Culture Trail: Cambodia & Laos",
                "destination": "Luang Prabang", "days": 10, "kind": "group",
                "price": "1590.00",
                "summary": "A cross-border cultural journey through Cambodia and Laos.",
                "description": "Connect two Mekong destinations through temples, river landscapes, heritage streets and local food. The route and border/flight connections are tailored to confirmed transport schedules.",
                "itinerary": "DAY 1 — ARRIVE PHNOM PENH: Welcome and hotel transfer.\n\nDAY 2 — PHNOM PENH: Guided introduction to royal and cultural landmarks.\n\nDAY 3 — SIEM REAP: Transfer to Siem Reap.\n\nDAY 4 — ANGKOR TEMPLES: Angkor Wat, Bayon and Ta Prohm.\n\nDAY 5 — SIEM REAP AT LEISURE: Optional Tonlé Sap or countryside excursion.\n\nDAY 6 — CONNECT TO LAOS: Travel to Luang Prabang via the confirmed flight/connection.\n\nDAY 7 — LUANG PRABANG HERITAGE: Royal Palace Museum area, Wat Xieng Thong and the old town.\n\nDAY 8 — KUANG SI WATERFALLS: Scenic countryside excursion and waterfall visit.\n\nDAY 9 — MEKONG RIVER EXPERIENCE: Optional river cruise and local craft visits.\n\nDAY 10 — DEPARTURE: Airport transfer.",
                "inclusions": "• 9 nights accommodation in selected hotels\n• Daily breakfast\n• Airport and intercity transfers stated in the final itinerary\n• Local English-speaking guides on scheduled touring days\n• Drinking water during touring\n• Cross-border itinerary coordination",
                "exclusions": "• International flights and regional flight tickets unless quoted in final offer\n• Visa fees and border charges\n• Angkor Pass, meals not stated, tips and insurance\n• Optional activities and personal expenses",
                "image": "/static/travel/images/destinations/luang_prabang.jpg",
            },
        ]
        for item in tours_data:
            Tour.objects.update_or_create(
                title=item["title"],
                defaults={
                    "destination": destinations[item["destination"]],
                    "duration_days": item["days"], "tour_type": item["kind"],
                    "price_per_person": Decimal(item["price"]),
                    "summary": item["summary"], "description": item["description"],
                    "itinerary": item["itinerary"], "inclusions": item["inclusions"],
                    "exclusions": item["exclusions"], "image_url": item["image"],
                    "max_group_size": 12, "is_active": True,
                },
            )

        hotels_data = [
            {
                "name": "Raffles Hotel Le Royal", "destination": "Phnom Penh",
                "stars": 5, "price": "220.00",
                "summary": "Historic Phnom Penh landmark with Khmer, French and Art Deco character.",
                "description": "A landmark heritage hotel dating to 1929, set in a leafy central Phnom Penh location. The property combines historic architecture with contemporary rooms, refined Khmer dining and the celebrated Elephant Bar.",
                "amenities": "Swimming pool and poolside terrace\nFitness centre and spa\nRestaurant Le Royal and Le Phnom 1929\nElephant Bar and afternoon tea\nWi-Fi\n24-hour personal butler service (hotel service; room/category terms apply)",
                "room_details": "Entry-level State Room categories are available in king or twin configurations. Room size, view, breakfast and cancellation terms vary by rate plan.",
                "image": "https://www.ahstatic.com/photos/a5e0_ho_00_p_2048x1536.jpg",
                "website": "https://www.raffles.com/phnom-penh/",
            },
            {
                "name": "Rosewood Phnom Penh", "destination": "Phnom Penh",
                "stars": 5, "price": "355.00",
                "summary": "Sky-high luxury in Vattanac Capital Tower with sweeping city and river views.",
                "description": "An ultra-luxury hotel occupying the upper floors of Vattanac Capital Tower in central Phnom Penh. Its contemporary rooms and suites, elevated dining, wellness facilities and skyline outlook make it a flagship city stay.",
                "amenities": "175 rooms and suites\nRestaurants, lounges and Sora sky bar\nSense, A Rosewood Spa\nFitness and indoor lap pool\nCity and Mekong views\nConcierge and private transfer options",
                "room_details": "Rooms and suites offer city views and residential-style furnishings. The displayed starting price is an indicative guide; inclusions depend on the selected offer.",
                "image": "https://static.bangkokpost.com/media/content/20230205/4633776.jpg",
                "website": "https://www.rosewoodhotels.com/en/phnom-penh",
            },
            {
                "name": "Park Hyatt Siem Reap", "destination": "Siem Reap",
                "stars": 5, "price": "200.00",
                "summary": "Contemporary luxury with a calm saltwater pool in the heart of Siem Reap.",
                "description": "A design-led luxury hotel in central Siem Reap, combining contemporary Khmer-inspired interiors with tranquil courtyard spaces. It is a convenient base for Old Market dining and excursions to Angkor.",
                "amenities": "Saltwater swimming pool\nSpa and wellness treatments\nFitness facilities\nOn-site dining\nConcierge and tour assistance\nWi-Fi",
                "room_details": "Multiple room and suite categories are offered. Breakfast, transfers and cancellation terms vary by selected rate.",
                "image": "https://www.yonder.fr/sites/default/files/styles/lg-insert/public/contenu/destinations/Park-Hyatt-Siem-Reap-Saltwater-Pool.jpg?itok=zwumtU3w",
                "website": "https://www.hyatt.com/park-hyatt/en-US/repgh-park-hyatt-siem-reap",
            },
            {
                "name": "Raffles Grand Hotel d'Angkor", "destination": "Siem Reap",
                "stars": 5, "price": "250.00",
                "summary": "A celebrated heritage hotel beside the Royal Independence Gardens.",
                "description": "A historic 1932 hotel with a classic colonial-era façade, tropical gardens and a strong sense of place. It offers a refined base for visiting the Angkor temples and Siem Reap town.",
                "amenities": "Outdoor swimming pool\nSpa and fitness facilities\nRestaurants and bars\nGarden and heritage architecture\nConcierge and tour assistance\nWi-Fi",
                "room_details": "Rooms and suites feature heritage-inspired design with modern comforts. Breakfast and transfers depend on the rate selected.",
                "image": "https://m.ahstatic.com/is/image/accorhotels/met_p_a081-01?dpr=on%2C2.625&qlt=82&ts=1771852171763&wid=575",
                "website": "https://www.raffles.com/siem-reap/",
            },
            {
                "name": "Shinta Mani Angkor", "destination": "Siem Reap",
                "stars": 5, "price": "180.00",
                "summary": "Boutique design hotel with a signature courtyard pool in Siem Reap.",
                "description": "A stylish boutique property in Siem Reap's French Quarter, known for distinctive design, attentive hospitality and easy access to the town centre and Angkor touring.",
                "amenities": "Courtyard swimming pool\nOn-site dining\nSpa and wellness options\nConcierge and guided excursion assistance\nWi-Fi\nSelected room and villa categories",
                "room_details": "Standard rooms and upgraded pool-villa categories are offered. The starting rate is an estimate and is not a live quote.",
                "image": "https://selectiveasia.tbxcdn.com/media/ef8b37655b-24b-0659/13369-800x600.jpg",
                "website": "https://shintamani.com/angkor/",
            },
            {
                "name": "Marina Bay Sands", "destination": "Singapore",
                "stars": 5, "price": "650.00",
                "summary": "Iconic integrated resort with a world-famous rooftop infinity pool.",
                "description": "A landmark Singapore resort known for its three-tower architecture, SkyPark, destination dining, shopping and entertainment. The rooftop infinity pool is reserved for registered hotel guests.",
                "amenities": "SkyPark rooftop infinity pool for hotel guests\nRestaurants and bars\nLuxury shopping and entertainment\nFitness and wellness facilities\nConvention and event spaces\nCity and bay views",
                "room_details": "Room categories and view types vary. Pool access is subject to hotel guest eligibility and operating rules. Rates vary significantly by date and demand.",
                "image": "https://i.insider.com/5cfed1e24cf27011b74cf93a?auto=webp&format=jpeg&width=800",
                "website": "https://www.marinabaysands.com/",
            },
            {
                "name": "Burj Al Arab Jumeirah", "destination": "Dubai",
                "stars": 5, "price": "1500.00",
                "summary": "Dubai's sail-shaped icon, known for suite-only luxury and private service.",
                "description": "An instantly recognizable luxury hotel set on its own island off Jumeirah Beach. The property is known for its sail-shaped architecture, expansive suite accommodation, signature dining and highly personalized hospitality.",
                "amenities": "Suite accommodation\nPrivate beach and pool experiences (access rules apply)\nSignature restaurants and lounges\nSpa and wellness facilities\nButler-style personalized service\nLuxury transfer options",
                "room_details": "All accommodations are suite categories with multiple layouts and sea views. Starting rate is a broad indicative estimate and can be substantially higher during peak periods.",
                "image": "https://media.cntraveler.com/photos/563126d4c406c560343dfdeb/master/pass/burj-al-arab-dubai-cr-alamy.jpg",
                "website": "https://www.jumeirah.com/en/stay/dubai/burj-al-arab-jumeirah",
            },
        ]
        for item in hotels_data:
            Hotel.objects.update_or_create(
                name=item["name"],
                defaults={
                    "destination": destinations[item["destination"]],
                    "category": item["stars"], "price_per_night": Decimal(item["price"]),
                    "summary": item["summary"], "description": item["description"],
                    "amenities": item["amenities"], "room_details": item["room_details"],
                    "image_url": item["image"], "website_url": item["website"],
                    "price_note": "Indicative starting guide in USD per room/night, not a live quote. Confirm exact dates, room type, taxes and inclusions before booking.",
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Professional demo destinations, detailed tour packages and hotel selections loaded. Verify rates and availability before selling."))
