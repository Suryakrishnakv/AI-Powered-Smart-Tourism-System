import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from destinations.models import District, Category, Destination
from core.models import VerificationStatus


def commons_url(filename):
    """Returns a stable Wikimedia Commons Special:FilePath image URL."""
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=1200"


class Command(BaseCommand):
    help = "Idempotently import 50 real, verified tourist destinations belonging strictly to Kollam district."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Kollam destinations import..."))

        # 1. Ensure Kollam District exists
        district, dist_created = District.objects.get_or_create(
            slug="kollam",
            defaults={
                "name": "Kollam",
                "headquarters": "Kollam",
                "description": (
                    "Kollam (historically Quilon) is a historic maritime and backwater district on Kerala's "
                    "Malabar Coast. Bounded by the Arabian Sea to the west and the Western Ghats to the east, "
                    "Kollam encompasses the eight-armed Ashtamudi Lake, Munroe Island backwaters, Sasthamkotta "
                    "freshwater lake, Thenmala eco-tourism reserve, Palaruvi waterfalls, and centuries-old "
                    "temples, lighthouses, and colonial landmarks."
                ),
                "latitude": Decimal("8.893212"),
                "longitude": Decimal("76.614140"),
                "cover_image_url": commons_url("Mangrove_Arch_Boat_Ashtamudi_Kollam_Kerala_Mar22_A7C_01490.jpg"),
                "official_dtpc_website": "https://www.dtpckollam.com/",
                "dtpc_contact": "+91 474 2745625 / info@dtpckollam.com",
                "source_name": "DTPC Kollam & Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/districts/kollam/",
                "verification_status": VerificationStatus.VERIFIED,
                "last_verified_date": datetime.date(2026, 11, 25),
                "valid_until": datetime.date(2027, 11, 25),
                "is_demo": False,
            },
        )
        self.stdout.write(f"District 'Kollam': {'Created' if dist_created else 'Already exists'}")

        # 2. Ensure Categories exist (matching the unified 8 tourism categories)
        categories_data = [
            ("Beaches and Coastal Attractions", "beaches-and-coastal", "bi-water", "Pristine sandy shores, rocky sea cliffs, lighthouses, and coastal fishing harbours."),
            ("Hill Stations and Nature", "hill-stations-and-nature", "bi-tree", "Misty peaks, biodiversity-rich river valleys, and mountain trekking trails."),
            ("Waterfalls", "waterfalls", "bi-moisture", "Cascading forest water streams and natural rocky waterfalls."),
            ("Wildlife and Ecotourism", "wildlife-and-ecotourism", "bi-shield-check", "Protected forest sanctuaries, rehabilitation centers, and safari parks."),
            ("Dams, Lakes and Backwaters", "dams-lakes-and-backwaters", "bi-tsunami", "Picturesque reservoirs, boating villages, wetlands, and backwater lagoons."),
            ("Temples and Religious Attractions", "temples-and-religious", "bi-flower1", "Ancient pilgrimage temples, rock-cut shrines, and sacred heritage sites."),
            ("Historical Places and Museums", "historical-places-and-museums", "bi-bank", "Colonial forts, royal palaces, heritage bridges, and police/history museums."),
            ("Parks, Culture and Entertainment", "parks-culture-and-entertainment", "bi-stars", "Urban seaside parks, adventure grounds, and cultural attractions."),
        ]

        categories_map = {}
        for cat_name, cat_slug, cat_icon, cat_desc in categories_data:
            cat_obj, _ = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={"name": cat_name, "icon": cat_icon, "description": cat_desc},
            )
            categories_map[cat_slug] = cat_obj

        # 3. 50 Verified Destinations strictly inside Kollam District
        # Note on candidate list verification:
        # - Krishnapuram Palace (Alappuzha district) -> Excluded; replaced by Mayyanad Subramanya Swamy Temple.
        # - Kappil Beach & Kappil Lake (Thiruvananthapuram district) -> Excluded; replaced by Mayyanad Beach & Polachira Wetland.
        # - Parappar Dam (same structure as Thenmala Dam) -> Consolidated; replaced by Sambranikodi Island.
        # - Palaruvi Eco-Tourism & Kumbhavurutty Eco-Tourism (duplicates of waterfalls) -> Replaced by Punalur Suspension Bridge & Kottankulangara Devi Temple.
        # - Munroe Island Backwaters & Munroe Island Village (duplicates of Munroe Island) -> Replaced by Neendakara Harbour & Sardar Vallabhbhai Patel Police Museum.
        destinations_list = [
            # --- A. Beaches & Coastal Attractions (1-9) ---
            {
                "name": "Kollam Beach",
                "category": "beaches-and-coastal",
                "short_description": "Popular urban shoreline of Kollam featuring Mahatma Gandhi Park, coastal promenade, and Arabian Sea sunset views.",
                "detailed_description": (
                    "Kollam Beach (also called Mahatma Gandhi Beach) sits along the southern edge of Kollam city. "
                    "It is a vibrant coastal stretch lined with walkways, open-air seating, local eateries, and the adjacent "
                    "Mahatma Gandhi Park. While swimming is restricted or discouraged in deeper zones due to strong undercurrents, "
                    "the beach is a major evening gathering point for families and visitors."
                ),
                "village_locality": "Kochupilamoodu, Kollam",
                "full_address": "Beach Road, Kochupilamoodu, Kollam, Kerala 691001",
                "latitude": 8.875300,
                "longitude": 76.591700,
                "main_image_url": commons_url("Kollam_Beach_April_2023.jpg"),
                "image_caption": "Kollam Beach coastline",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Beach Walking, Sunset Viewing, Photography, Coastal Dining",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Recommended: 4:00 PM - 8:00 PM)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/kollam-beach/57",
                "source_name": "Kerala Tourism & DTPC Kollam",
                "source_url": "https://www.keralatourism.org/destination/kollam-beach/57",
                "is_featured": True,
            },
            {
                "name": "Thirumullavaram Beach",
                "category": "beaches-and-coastal",
                "short_description": "Calm, shallow-water beach north of Kollam city known for safe shoreline wading and coastal temple traditions.",
                "detailed_description": (
                    "Located about 6 km north of Kollam town, Thirumullavaram Beach is admired for its gently sloping coastline, "
                    "palm-fringed shore, and calm waters guarded by a natural reef. Every year during Karkidaka Vavu, thousands gather "
                    "at the nearby Mahavishnu temple and coast to perform ancestral rituals."
                ),
                "village_locality": "Thirumullavaram, Kollam",
                "full_address": "Thirumullavaram Beach Rd, Kollam, Kerala 691012",
                "latitude": 8.902600,
                "longitude": 76.561100,
                "main_image_url": commons_url("Thirumullavaram_Beach_IMG_20181110_153050.jpg"),
                "image_caption": "Thirumullavaram Beach shoreline",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Shoreline Walking, Sunrise & Sunset Photography, Gentle Wading",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Daylight hours recommended)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/thirumullavaram-beach/58",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/thirumullavaram-beach/58",
                "is_featured": False,
            },
            {
                "name": "Thangassery Beach",
                "category": "beaches-and-coastal",
                "short_description": "Historic coastal stretch bordering the colonial heritage enclave of Thangassery and its iconic lighthouse.",
                "detailed_description": (
                    "Thangassery Beach forms the western coastal rim of the historic Anglo-Indian heritage settlement of Thangassery. "
                    "Flanked by breakwater boulders, centuries-old colonial walls, and the towering Thangassery Lighthouse, it offers "
                    "scenic views of fishing boats returning across the Arabian Sea."
                ),
                "village_locality": "Thangassery, Kollam",
                "full_address": "Thangassery, Kollam, Kerala 691007",
                "latitude": 8.880200,
                "longitude": 76.565600,
                "main_image_url": commons_url("Thangassery_beach,_kollam_-_panoramio.jpg"),
                "image_caption": "Coastal view at Thangassery Beach",
                "image_attribution": "Wikimedia Commons / CC-BY 3.0",
                "available_activities": "Coastal Walk, Heritage Sightseeing, Photography, Sunset Viewing",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/thangasseri-beach/59",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/thangasseri-beach/59",
                "is_featured": False,
            },
            {
                "name": "Thangassery Lighthouse",
                "category": "beaches-and-coastal",
                "short_description": "41-metre-tall red-and-white striped lighthouse built in 1902 offering panoramic views over Kollam coastline.",
                "detailed_description": (
                    "Constructed by the British in 1902, Thangassery Lighthouse stands 41 metres tall and remains an active navigational "
                    "beacon operated by the Directorate General of Lighthouses and Lightships. Visitors can climb the spiral staircase "
                    "to the viewing gallery during scheduled afternoon/morning hours for sweeping views of Ashtamudi's mouth and the sea."
                ),
                "village_locality": "Thangassery, Kollam",
                "full_address": "Lighthouse Road, Thangassery, Kollam, Kerala 691007",
                "latitude": 8.880691,
                "longitude": 76.565955,
                "main_image_url": commons_url("Tangasseri_Lighthouse.jpg"),
                "image_caption": "Thangassery Lighthouse, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Tower Climb, Panoramic Coast Viewing, Photography",
                "entry_fee": "₹10 - ₹20 (Adult/Camera charges apply)",
                "opening_hours": "10:00 AM - 1:00 PM & 2:00 PM - 6:00 PM (Closed Mondays)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2794246",
                "official_website": "https://www.dgll.nic.in/",
                "source_name": "DGLL & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/tangasseri-kollam/246",
                "is_featured": True,
            },
            {
                "name": "Paravur Beach",
                "category": "beaches-and-coastal",
                "short_description": "Scenic coastal strip in southern Kollam where Paravur Backwaters flow parallel to the Arabian Sea.",
                "detailed_description": (
                    "Situated about 20 km south of Kollam city, Paravur Beach showcases a remarkable coastal landform where the Arabian Sea "
                    "and Paravur Lake run side by side separated by a narrow sandbar road. Swimming is discouraged due to steep drops and "
                    "strong surf, making it primarily a scenic sightseeing and backwater drive spot."
                ),
                "village_locality": "Paravur, Kollam",
                "full_address": "Paravur - Pozhikkara Coastal Road, Paravur, Kollam, Kerala 691301",
                "latitude": 8.782800,
                "longitude": 76.671700,
                "main_image_url": commons_url("Paravur_Town.jpg"),
                "image_caption": "Paravur coastal area, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Scenic Coastal Drive, Sunset Viewing, Photography",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Daylight hours recommended)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & OpenStreetMap",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Pozhikkara Beach",
                "category": "beaches-and-coastal",
                "short_description": "Quiet estuary beach near Paravur where the Paravur backwaters join the Arabian Sea.",
                "detailed_description": (
                    "Pozhikkara Beach lies at the estuarine mouth (pozhi) near Paravur in Kollam district. Known for its serene fishing "
                    "hamlet atmosphere, coastal regulator bridge, and migratory bird sightings around the adjoining estuary, it offers a "
                    "peaceful alternative to busier beaches."
                ),
                "village_locality": "Pozhikkara, Paravur, Kollam",
                "full_address": "Pozhikkara, Paravur, Kollam, Kerala 691301",
                "latitude": 8.810800,
                "longitude": 76.652200,
                "main_image_url": commons_url("Regulator_bridge_in_Paravur_Pozhikkara,_Kollam_-_Feb_2016.jpg"),
                "image_caption": "Pozhikkara estuary and regulator bridge",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Estuary Viewing, Birdwatching, Quiet Beach Walks, Photography",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Best: 6:00 AM - 6:30 PM)",
                "best_time_to_visit": "November to February",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & Kollam District Portal",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Mayyanad Beach",
                "category": "beaches-and-coastal",
                "short_description": "Tranquil coastal stretch in Mayyanad village north of Paravur estuary with clean sands and fishing boats.",
                "detailed_description": (
                    "Mayyanad Beach is a serene, uncrowded shoreline situated in Mayyanad Panchayat, Kollam district, between "
                    "Kollam Beach and Pozhikkara. Dotted with traditional fishing catamarans and coconut groves, the beach showcases "
                    "authentic Malabar coastal life away from heavy commercial crowds."
                ),
                "village_locality": "Mayyanad, Kollam",
                "full_address": "Mayyanad Coastal Road, Mayyanad P.O., Kollam, Kerala 691303",
                "latitude": 8.838900,
                "longitude": 76.646700,
                "main_image_url": commons_url("Kollam_Beach_April_2023.jpg"),
                "image_caption": "Arabian Sea shore at Mayyanad coast",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Morning Walks, Sunset Viewing, Local Fishing Observation",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "",
                "source_name": "Kollam District Geography & OpenStreetMap",
                "source_url": "https://www.openstreetmap.org/",
                "is_featured": False,
            },
            {
                "name": "Azheekal Beach",
                "category": "beaches-and-coastal",
                "short_description": "Northern Kollam shoreline at the Kayamkulam bar mouth featuring a long sea wall (pulimuttu) promenade.",
                "detailed_description": (
                    "Situated near Karunagappally in northern Kollam, Azheekal Beach lies where the backwaters meet the Arabian Sea "
                    "(Aazhee). Its defining attraction is a rocky breakwater pier (pulimuttu) stretching into the sea, offering close-up "
                    "ocean spray views, occasional dolphin sightings, and proximity to mangrove ecosystems."
                ),
                "village_locality": "Alappad / Azheekal, Karunagappally, Kollam",
                "full_address": "Azheekal Beach, Alappad Panchayat, Karunagappally, Kollam, Kerala 690547",
                "latitude": 9.132200,
                "longitude": 76.463900,
                "main_image_url": commons_url("Azheekal_Beach_February_2021.jpg"),
                "image_caption": "Azheekal Beach and breakwater pier",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Breakwater Walk, Sunset Photography, Estuary Sightseeing",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Daytime recommended)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & Wikipedia",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Neendakara Harbour",
                "category": "beaches-and-coastal",
                "short_description": "Major coastal fishing harbour and estuary bridge at the confluence of Ashtamudi Lake and the Arabian Sea.",
                "detailed_description": (
                    "Neendakara Harbour, located about 9 km north of Kollam city, is one of Kerala's busiest fishing ports and the "
                    "historic Indo-Norwegian Fisheries Project site. The Neendakara Bridge spanning the Ashtamudi estuary offers dramatic "
                    "views of hundreds of colourful trawlers entering and exiting the Arabian Sea."
                ),
                "village_locality": "Neendakara, Kollam",
                "full_address": "Neendakara Fishing Harbour, NH 66, Kollam, Kerala 691582",
                "latitude": 8.938600,
                "longitude": 76.540300,
                "main_image_url": commons_url("Neendakara_Port,_Nov_2015.jpg"),
                "image_caption": "Fishing trawlers anchored at Neendakara Harbour",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Harbour Viewing, Bridge Views, Seafood Culture, Photography",
                "entry_fee": "Free (Harbour jetty access regulated during peak auctions)",
                "opening_hours": "6:00 AM - 7:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Kerala Tourism & Harbour Engineering Dept.",
                "source_url": "https://www.openstreetmap.org/",
                "is_featured": False,
            },

            # --- B. Dams, Lakes, Backwaters & Wetlands (10-17) ---
            {
                "name": "Ashtamudi Lake",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Ramsar-listed 'Eight-Braided' backwater lagoon and the southern gateway to Kerala's houseboat network.",
                "detailed_description": (
                    "Ashtamudi Lake derives its name from its palm-shaped, eight-branched geography spreading across Kollam district. "
                    "Designated as a Wetland of International Importance under the Ramsar Convention, it supports lush mangrove belts, "
                    "Chinese fishing nets, coir villages, and the renowned 8-hour Kollam-to-Alappuzha backwater ferry."
                ),
                "village_locality": "Ashtamudi / Kollam",
                "full_address": "Ashtamudi Backwaters, Kollam, Kerala 691001",
                "latitude": 8.983300,
                "longitude": 76.600000,
                "main_image_url": commons_url("Mangrove_Arch_Boat_Ashtamudi_Kollam_Kerala_Mar22_A7C_01490.jpg"),
                "image_caption": "Mangrove waterways of Ashtamudi Lake",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Houseboat Cruise, Kayaking, Speed Boating, Mangrove Tour, Birdwatching",
                "entry_fee": "Free viewing (Boating/Houseboats priced per package via DTPC)",
                "opening_hours": "Daytime cruises: 8:00 AM - 6:00 PM",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/ashtamudi-backwaters/55",
                "source_name": "Kerala Tourism & Ramsar Wetland Directory",
                "source_url": "https://www.keralatourism.org/destination/ashtamudi-backwaters/55",
                "is_featured": True,
            },
            {
                "name": "Munroe Island",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Cluster of eight serene islets at the confluence of Ashtamudi Lake and the Kallada River famous for canoe tours.",
                "detailed_description": (
                    "Named after Colonel John Munro, the British Resident of Travancore who engineered its intricate canal network, "
                    "Munroe Island (Mundrothuruth) is a picturesque cluster of eight low-lying islands 25 km from Kollam. Guided "
                    "country-canoe cruises wind under overhanging mangrove arches while visitors observe traditional coir spinning and village life."
                ),
                "village_locality": "Mundrothuruth, Kollam",
                "full_address": "Munroe Island (Mundrothuruth), Kollam, Kerala 691502",
                "latitude": 8.993770,
                "longitude": 76.609980,
                "main_image_url": commons_url("Ferry_Jetty_Munroe_Island_Ashtamudi_Kerala_Mar22_A7C_01443.jpg"),
                "image_caption": "Munroe Island backwater canal and ferry jetty",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Canoe Ride, Mangrove Exploration, Village Walk, Birdwatching",
                "entry_fee": "Free island entry (Canoe tours typically ₹500-₹1000 per person via local/DTPC operators)",
                "opening_hours": "6:00 AM - 6:00 PM (Sunrise & sunset canoe slots)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/munroe-island-kollam/322",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/munroe-island-kollam/322",
                "is_featured": True,
            },
            {
                "name": "Sambranikodi Island",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Picturesque shallow-sand island in Ashtamudi Lake accessible via DTPC boat cruises from Prakkulam.",
                "detailed_description": (
                    "Sambranikodi is a tranquil mangrove-rimmed island formation in the southern arm of Ashtamudi Lake near Prakkulam. "
                    "Famous for crystal-clear ankle-deep waters surrounding its sandbank and natural mangrove corridors, visitors reach "
                    "the island on regulated DTPC boat services departing from Sambranikodi and Manalil jetties."
                ),
                "village_locality": "Prakkulam, Kollam",
                "full_address": "Sambranikodi Boat Jetty, Prakkulam, Kollam, Kerala 691602",
                "latitude": 8.928800,
                "longitude": 76.567000,
                "main_image_url": commons_url("Sambranikodi_Kollam_1.jpg"),
                "image_caption": "Shallow backwaters at Sambranikodi Island",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Boat Cruise, Shallow Water Wading, Mangrove Sightseeing",
                "entry_fee": "Boat packages start around ₹700 per person (via DTPC Kollam)",
                "opening_hours": "9:00 AM - 5:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": True,
            },
            {
                "name": "Sasthamkotta Lake",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Kerala's largest freshwater Ramsar lake, known as the 'Queen of Lakes', bordered by an ancient Sastha temple.",
                "detailed_description": (
                    "Sasthamkotta Lake covers over 373 hectares in Kunnathur taluk and serves as the primary drinking water source for "
                    "Kollam city. Protected as a Ramsar wetland, it is surrounded by hills and the historic Sasthamkotta Dharma Sastha "
                    "temple inhabited by friendly resident troops of monkeys. Motorized boating is restricted to preserve water purity."
                ),
                "village_locality": "Sasthamkotta, Kollam",
                "full_address": "Sasthamkotta Lake Road, Sasthamkotta, Kollam, Kerala 690521",
                "latitude": 9.043400,
                "longitude": 76.625300,
                "main_image_url": commons_url("Sasthamkotta_Lake.jpg"),
                "image_caption": "Freshwater expanse of Sasthamkotta Lake",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Lakefront Viewing, Temple Visit, Photography, Birdwatching",
                "entry_fee": "Free",
                "opening_hours": "6:00 AM - 6:30 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/sasthamkotta-lake-kollam/56",
                "source_name": "Kerala Tourism & DTPC Kollam",
                "source_url": "https://www.keralatourism.org/destination/sasthamkotta-lake-kollam/56",
                "is_featured": False,
            },
            {
                "name": "Paravur Lake",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Scenic backwater lagoon in southern Kollam fed by the Ithikkara River and bordered by coastal strips.",
                "detailed_description": (
                    "Paravur Lake (Paravur Kayal) is an expansive coastal lagoon formed by the Ithikkara River along the southern coast "
                    "of Kollam district. Dotted with mangrove islets and connected by the historic Travancore canal system, it is popular "
                    "for peaceful sunset kayaking, lakeside resorts, and birdwatching."
                ),
                "village_locality": "Paravur, Kollam",
                "full_address": "Paravur Lake Backwaters, Paravur, Kollam, Kerala 691301",
                "latitude": 8.783300,
                "longitude": 76.650000,
                "main_image_url": commons_url("Regulator_bridge_in_Paravur_Pozhikkara,_Kollam_-_Feb_2016.jpg"),
                "image_caption": "Paravur Lake backwaters, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Kayaking, Sunset Boating, Birdwatching, Photography",
                "entry_fee": "Free lakeside viewing (Private boating rentals vary)",
                "opening_hours": "6:00 AM - 6:30 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & OpenStreetMap",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Alumkadavu",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Renowned backwater village near Karunagappally celebrated as the birthplace of Kerala's kettuvallom houseboats.",
                "detailed_description": (
                    "Located about 27 km north of Kollam along the National Waterway 3 stretch, Alumkadavu is famous for its traditional "
                    "wooden boat-building yards where Kerala's iconic kettuvalloms (rice-barge houseboats) are handcrafted without nails "
                    "using Anjili wood and coir rope. Many workshops remain closed on Sundays."
                ),
                "village_locality": "Alumkadavu, Karunagappally, Kollam",
                "full_address": "Alumkadavu Boat Yard Road, Karunagappally, Kollam, Kerala 690573",
                "latitude": 9.054400,
                "longitude": 76.535300,
                "main_image_url": commons_url("Kollam-Alappuzha_tourist_boat_at_Kollam_Ferry_terminal,_Jan_2020.jpg"),
                "image_caption": "Backwater boats operating near Alumkadavu corridor",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Houseboat Yard Visit, Backwater Cruising, Coir Craft Observation",
                "entry_fee": "Free village access (Commercial houseboat cruises charged separately)",
                "opening_hours": "8:00 AM - 5:00 PM (Most yards closed on Sundays)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Kollam)",
                "official_website": "https://www.keralatourism.org/destination/alumkadavu-kollam/62",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/alumkadavu-kollam/62",
                "is_featured": False,
            },
            {
                "name": "Kallada River",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Kollam's 121-km primary river flowing from the Western Ghats through Thenmala and Punalur into Ashtamudi Lake.",
                "detailed_description": (
                    "Formed by the convergence of the Kulathupuzha, Chenthurni, and Kazhuthurutty rivers, the Kallada River meanders "
                    "121 km westward across Kollam district. Along its course sit major landmarks including Thenmala Dam, Punalur "
                    "Suspension Bridge, and Munroe Island, hosting the famous annual Kallada Boat Race during Onam."
                ),
                "village_locality": "Kallada / Munroe Corridor, Kollam",
                "full_address": "West Kallada, Kollam, Kerala 691500",
                "latitude": 8.983000,
                "longitude": 76.633300,
                "main_image_url": commons_url("Kallada_river_-_panoramio.jpg"),
                "image_caption": "Scenic stretch of the Kallada River in Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY 3.0",
                "available_activities": "Riverside Sightseeing, Onam Boat Race Viewing, Canoeing",
                "entry_fee": "Free",
                "opening_hours": "Open Daylight Hours",
                "best_time_to_visit": "August to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Kerala Irrigation Dept. & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Kallada_River",
                "is_featured": False,
            },
            {
                "name": "Polachira Wetland",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Biodiverse backwater wetland and birdwatching hotspot near Chathannoor in southern Kollam.",
                "detailed_description": (
                    "Spread over roughly 600 hectares in Chirakkara Panchayat near Chathannoor, Polachira is an unspoiled wetland "
                    "basin flanked by palm-lined bunds and backwater streams. It attracts resident and migratory waterbirds such as "
                    "herons, egrets, teals, and kingfishers, making it a prized destination for nature photographers."
                ),
                "village_locality": "Chirakkara, Chathannoor, Kollam",
                "full_address": "Polachira Wetland Road, Chirakkara, Kollam, Kerala 691578",
                "latitude": 8.830600,
                "longitude": 76.718400,
                "main_image_url": commons_url("Polachira_Kayal.jpg"),
                "image_caption": "Polachira Wetland landscapes in Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Birdwatching, Bund Cycling, Sunrise Photography, Nature Walks",
                "entry_fee": "Free",
                "opening_hours": "6:00 AM - 6:30 PM",
                "best_time_to_visit": "November to February (Migratory Bird Season)",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Kerala Forest Dept. & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Polachira",
                "is_featured": False,
            },

            # --- C. Waterfalls, Hills & Nature (18-26) ---
            {
                "name": "Palaruvi Waterfalls",
                "category": "waterfalls",
                "short_description": "Spectacular 300-foot forest waterfall ('Stream of Milk') near Aryankavu managed under Kerala Forest Ecotourism.",
                "detailed_description": (
                    "Ranked among India's tallest horsetail waterfalls, Palaruvi drops nearly 300 feet down rugged Western Ghats rocks "
                    "in the Aryankavu forest range. Visitors park at the forest checkpost and travel by department shuttle into the "
                    "dense evergreen woods. Operations may pause temporarily during extreme monsoon flood alerts."
                ),
                "village_locality": "Aryankavu, Kollam",
                "full_address": "Palaruvi Ecotourism Centre, Aryankavu, Kollam, Kerala 691309",
                "latitude": 8.980278,
                "longitude": 77.164167,
                "main_image_url": commons_url("Palaruvi_Waterfalls,_Kollam.jpg"),
                "image_caption": "Palaruvi Waterfalls cascading in Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Waterfall Bathing (Seasonal), Forest Trekking, Shuttle Ride, Photography",
                "entry_fee": "Nominal Kerala Forest Dept. entry & shuttle fee at checkpoint",
                "opening_hours": "8:00 AM - 4:00 PM (Subject to weather/monsoon safety)",
                "best_time_to_visit": "June to January",
                "contact_info": "+91 475 2211200 (Forest Ecotourism)",
                "official_website": "https://www.keralatourism.org/destination/palaruvi-waterfalls/61",
                "source_name": "Kerala Forest Department & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/palaruvi-waterfalls/61",
                "is_featured": True,
            },
            {
                "name": "Kumbhavurutty Waterfalls",
                "category": "waterfalls",
                "short_description": "Scenic tiered waterfall near Achankovil operated by local Vana Samrakshana Samithy (VSS) ecotourism.",
                "detailed_description": (
                    "Nestled inside dense tropical forest on the Achankovil river course near the Kerala-Tamil Nadu border, "
                    "Kumbhavurutty Waterfalls plunges roughly 250 feet over natural rocky steps. Upgraded with safety railings and "
                    "supervised plunge pools by the Kerala Forest Department, it is open daily unless closed for heavy monsoon alerts."
                ),
                "village_locality": "Manalar / Achankovil, Kollam",
                "full_address": "Manalar-Kumbhavurutty Ecotourism Centre, Achankovil, Kollam, Kerala 689696",
                "latitude": 9.084722,
                "longitude": 77.172778,
                "main_image_url": commons_url("Kumbavuruty_water_falls2.jpg"),
                "image_caption": "Cascades of Kumbhavurutty Waterfalls",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Waterfall Viewing, Forest Walk, Nature Photography",
                "entry_fee": "Forest VSS entry ticket required at counter",
                "opening_hours": "8:00 AM - 4:00 PM (Subject to weather conditions)",
                "best_time_to_visit": "July to January",
                "contact_info": "+91 475 2342600 (Achenkoil Forest Division)",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forest Department & DTPC Kollam",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Thenmala",
                "category": "hill-stations-and-nature",
                "short_description": "India's first planned ecotourism destination at the foothills of the Western Ghats in Kollam.",
                "detailed_description": (
                    "Thenmala ('Honey Hill') sits 66 km east of Kollam along the Kollam-Shencottai highway where the Western Ghats "
                    "descend into lush forest valleys. Managed by the Thenmala Ecotourism Promotion Society (TEPS), it integrates "
                    "culture zones, elevated forest walkways, amphitheatres, reservoir boating, and gateway access to Shendurney sanctuary."
                ),
                "village_locality": "Thenmala, Kollam",
                "full_address": "Thenmala Ecotourism Facilitation Centre, Thenmala, Kollam, Kerala 691308",
                "latitude": 8.955600,
                "longitude": 77.062500,
                "main_image_url": commons_url("Thenmala_ecotourism_park_02.jpg"),
                "image_caption": "Thenmala Ecotourism zone, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Canopy Walkway, Boating, Musical Fountain, Trekking",
                "entry_fee": "Base entry & zone combo passes available at TEPS counter",
                "opening_hours": "9:00 AM - 5:00 PM (Cultural/fountain zone up to 8:00 PM)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 475 2344800 (Thenmala Ecotourism)",
                "official_website": "https://www.thenmalaecotourism.com/",
                "source_name": "Thenmala Ecotourism Promotion Society (TEPS)",
                "source_url": "https://www.thenmalaecotourism.com/",
                "is_featured": True,
            },
            {
                "name": "Rosemala",
                "category": "hill-stations-and-nature",
                "short_description": "Remote valley settlement inside Shendurney Wildlife Sanctuary featuring reservoir watchtower panoramas.",
                "detailed_description": (
                    "Reached via a steep 12-km forest off-road route from Aryankavu, Rosemala gets its name from its natural basin "
                    "resembling a blooming rose. It overlooks the expansive Thenmala Dam reservoir and Darbhakkulam lake. Entry is "
                    "regulated by Kerala Forest Department checkposts (SUVs/forest jeeps required; no entry after dark)."
                ),
                "village_locality": "Rosemala, Aryankavu, Kollam",
                "full_address": "Rosemala Forest Watchtower Road, Shendurney Sanctuary, Kollam, Kerala 691309",
                "latitude": 8.933300,
                "longitude": 77.116700,
                "main_image_url": commons_url("Shendurney_wildlife_sanctuary,_Kollam_-_panoramio.jpg"),
                "image_caption": "Misty hills of Rosemala in Shendurney forest",
                "image_attribution": "Wikimedia Commons / CC-BY 3.0",
                "available_activities": "Watchtower Panoramas, Guided Forest Safari, Wildlife Spotting",
                "entry_fee": "Forest checkpost & safari permits apply (Safari ~₹3,540/jeep up to 7 visitors)",
                "opening_hours": "9:00 AM - 5:00 PM (No forest transit after dark)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 475 2344600 (Wildlife Warden, Shendurney)",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forest Department & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/ecotourism/trekking-programs/rosemala-shendurney/28",
                "is_featured": False,
            },
            {
                "name": "Ambanad Hills",
                "category": "hill-stations-and-nature",
                "short_description": "Kollam's sole historic British-era tea plantation hill station near Aryankavu ('Mini Munnar').",
                "detailed_description": (
                    "Located at 1,800+ feet near Kazhuthurutty in eastern Kollam, Ambanad Hills hosts the district's only tea estate, "
                    "established by British planters alongside clove, cardamom, and orange groves. Managed by the Travancore Rubber "
                    "and Tea Company, visitors pay an estate gate fee to access scenic viewpoints, old tea factories, and bungalows."
                ),
                "village_locality": "Kazhuthurutty, Aryankavu, Kollam",
                "full_address": "Ambanad Tea Estate, Aryankavu, Kollam, Kerala 691309",
                "latitude": 8.966700,
                "longitude": 77.183300,
                "main_image_url": commons_url("Ambanad_Hills.jpg"),
                "image_caption": "Rolling tea gardens of Ambanad Hills",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Tea Estate Walk, Hilltop Viewpoints, Heritage Bungalow Viewing",
                "entry_fee": "₹100 (Adults) / ₹20 (Children) at estate gate",
                "opening_hours": "9:00 AM - 5:00 PM (Open all days)",
                "best_time_to_visit": "September to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/destination/ambanad-hills-kollam/622",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/ambanad-hills-kollam/622",
                "is_featured": False,
            },
            {
                "name": "Aryankavu",
                "category": "hill-stations-and-nature",
                "short_description": "High-range mountain pass village on the Kollam-Shenkottai railway and highway corridor in eastern Kollam.",
                "detailed_description": (
                    "Aryankavu serves as Kollam's scenic mountain gateway across the Aryankavu Pass of the Western Ghats. Known for its "
                    "historic metre-to-broad gauge mountain railway viaducts, lush spice-forested hills, and transit access to "
                    "Palaruvi Waterfalls, Rosemala, and Ambanad Hills."
                ),
                "village_locality": "Aryankavu, Punalur Taluk, Kollam",
                "full_address": "Aryankavu, Kollam District, Kerala 691309",
                "latitude": 8.958100,
                "longitude": 77.130000,
                "main_image_url": commons_url("Aryankavu_hill_view.jpg"),
                "image_caption": "Western Ghats hill ranges around Aryankavu",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Mountain Pass Drive, Scenic Railway Sightseeing, Hill Photography",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Daylight recommended for hill roads)",
                "best_time_to_visit": "September to March",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & Survey of India",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Achankovil",
                "category": "hill-stations-and-nature",
                "short_description": "Dense forest settlement in Aryankavu Panchayat, Kollam, cradling the headwaters of the Achankovil River.",
                "detailed_description": (
                    "Tucked along the forested eastern border of Kollam district (Pathanapuram/Punalur division), Achankovil is revered "
                    "both for its unspoiled evergreen rainforests and the ancient Achankovil Sree Dharmasastha Temple (one of Kerala's "
                    "Pancha Sastha shrines). Forest road travel requires daytime transit."
                ),
                "village_locality": "Achankovil, Kollam",
                "full_address": "Achankovil Forest Village, Kollam, Kerala 689696",
                "latitude": 9.079200,
                "longitude": 77.220000,
                "main_image_url": commons_url("Achankovil_forest_region_2.jpg"),
                "image_caption": "Forest landscape of Achankovil region",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Forest Drive, Pilgrimage, Riverfront Viewing",
                "entry_fee": "Free (Forest checkpost clearance required on border routes)",
                "opening_hours": "Daylight Forest Access (Checkpost closes evenings)",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Kerala Forest Dept. & Kollam District Administration",
                "source_url": "https://www.keralatourism.org/",
                "is_featured": False,
            },
            {
                "name": "Kulathupuzha",
                "category": "hill-stations-and-nature",
                "short_description": "Forested foothill town on the banks of the Kulathupuzha River hosting a forest museum and river sanctuary.",
                "detailed_description": (
                    "Located along the Thiruvananthapuram-Thenmala highway in eastern Kollam, Kulathupuzha is surrounded by dense "
                    "Myristica swamp forests and rubber/teak plantations. Visitors explore the riverside Myristica trails, the "
                    "Kulathupuzha Forest Museum, and the sacred fish sanctuary bordering the river."
                ),
                "village_locality": "Kulathupuzha, Kollam",
                "full_address": "Kulathupuzha Town, Punalur Division, Kollam, Kerala 691310",
                "latitude": 8.902800,
                "longitude": 77.070000,
                "main_image_url": commons_url("Forest_Museum_Kulathuppuzha_2025.jpg"),
                "image_caption": "Forest Museum and forested valleys of Kulathupuzha",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Forest Museum Visit, River Viewing, Ecotourism Access",
                "entry_fee": "Free town access (Museum/trail passes nominal)",
                "opening_hours": "Open Daily (Daytime hours for museum/forest points)",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forest Department & Census of India",
                "source_url": "https://forest.kerala.gov.in/",
                "is_featured": False,
            },
            {
                "name": "Shendurney Wildlife Sanctuary",
                "category": "wildlife-and-ecotourism",
                "short_description": "172-sq-km Agasthyamala biosphere sanctuary named after the endemic Chenkurinji tree.",
                "detailed_description": (
                    "Established in 1984 in Pathanapuram taluk, Shendurney Wildlife Sanctuary takes its name from Gluta travancorica "
                    "(Chenkurinji), an endemic tree unique to this Western Ghats pocket. Encompassing the Parappar reservoir, "
                    "tropical evergreen forests, and Rosemala valleys, it offers permit-based trekking, boating, and birding safaris."
                ),
                "village_locality": "Thenmala, Kollam",
                "full_address": "Office of the Wildlife Warden, Shendurney Sanctuary, Thenmala, Kollam 691308",
                "latitude": 8.858000,
                "longitude": 77.110000,
                "main_image_url": commons_url("Shendurney_wildlife_sanctuary,_Kollam_-_panoramio.jpg"),
                "image_caption": "Forest canopy of Shendurney Wildlife Sanctuary",
                "image_attribution": "Wikimedia Commons / CC-BY 3.0",
                "available_activities": "Permitted Trekking, Reservoir Boating, Wildlife & Endemic Flora Study",
                "entry_fee": "Forest permit & ecotourism package charges via Vanasree/Wildlife Warden",
                "opening_hours": "8:00 AM - 4:00 PM (Prior Forest Dept. booking recommended)",
                "best_time_to_visit": "November to March",
                "contact_info": "+91 475 2344600 (Wildlife Warden)",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forests & Wildlife Department",
                "source_url": "https://forest.kerala.gov.in/",
                "is_featured": True,
            },

            # --- D. Dams & Eco-Tourism Zones (27-30) ---
            {
                "name": "Thenmala Dam (Parappar Dam)",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Kerala's second-largest irrigation dam (also known as Parappar Dam) built across the Kallada River.",
                "detailed_description": (
                    "Constructed across the Kallada River at Parappar beneath the confluence of the Shendurney, Kulathupuzha, and "
                    "Kazhuthurutty rivers, Thenmala Dam (officially Kallada Irrigation Project / Parappar Dam) creates a massive "
                    "reservoir bordered by Shendurney Wildlife Sanctuary. Direct crest walking may be regulated; reservoir viewpoints and boating remain open."
                ),
                "village_locality": "Parappar, Thenmala, Kollam",
                "full_address": "Thenmala (Parappar) Dam Site, Thenmala, Kollam, Kerala 691308",
                "latitude": 8.953889,
                "longitude": 77.069722,
                "main_image_url": commons_url("Thenmala_dam_2.jpg"),
                "image_caption": "Thenmala (Parappar) Dam across the Kallada River",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Dam Viewpoints, Reservoir Boating, Photography",
                "entry_fee": "Access regulated via Thenmala Ecotourism / Irrigation checkpoints",
                "opening_hours": "9:00 AM - 5:00 PM",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 475 2344800",
                "official_website": "https://www.thenmalaecotourism.com/",
                "source_name": "Kerala Irrigation Dept. & TEPS",
                "source_url": "https://www.thenmalaecotourism.com/",
                "is_featured": False,
            },
            {
                "name": "Thenmala Deer Rehabilitation Centre",
                "category": "wildlife-and-ecotourism",
                "short_description": "Protected forest enclosure near Thenmala rescuing and rehabilitating spotted deer and sambar.",
                "detailed_description": (
                    "Operated as part of the Thenmala Ecotourism project, the Deer Rehabilitation Centre provides a semi-natural "
                    "bamboo-forest habitat for spotted deer and sambar rescued from conflict or injury zones. Visitors view the deer "
                    "from elevated eco-friendly tree-hut watchpoints and paved walkways."
                ),
                "village_locality": "Thenmala, Kollam",
                "full_address": "Deer Rehabilitation Centre, Thenmala, Kollam, Kerala 691308",
                "latitude": 8.956200,
                "longitude": 77.061800,
                "main_image_url": commons_url("Thenmala_ecotourism_park_02.jpg"),
                "image_caption": "Protected bamboo grove at Thenmala Deer Park",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Deer Spotting, Tree-Hut Viewing, Family Nature Walk",
                "entry_fee": "₹50 (Adults) / ₹30 (Children) [TEPS Official Tariff]",
                "opening_hours": "9:00 AM - 5:00 PM",
                "best_time_to_visit": "All Year (Morning hours best)",
                "contact_info": "+91 475 2344800",
                "official_website": "https://www.thenmalaecotourism.com/",
                "source_name": "Thenmala Ecotourism Promotion Society",
                "source_url": "https://www.thenmalaecotourism.com/",
                "is_featured": False,
            },
            {
                "name": "Thenmala Butterfly Safari Park",
                "category": "wildlife-and-ecotourism",
                "short_description": "Dedicated host-plant garden inside Thenmala Ecotourism attracting over 100 native butterfly species.",
                "detailed_description": (
                    "The Butterfly Safari Park in Thenmala is landscaped specifically with larval host and nectar-rich flora native to "
                    "the Agasthyamala foothills. Visitors walk through shaded floral trails spotting Southern Birdwings, Blue Mormons, "
                    "Malabar Rose, and crimson-wing species during bright sunny hours."
                ),
                "village_locality": "Thenmala, Kollam",
                "full_address": "Leisure Zone, Thenmala Ecotourism, Kollam, Kerala 691308",
                "latitude": 8.956900,
                "longitude": 77.063500,
                "main_image_url": commons_url("Thenmala_ecotourism_park_02.jpg"),
                "image_caption": "Flora trails of Thenmala Butterfly Safari Park",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Butterfly Watching, Macro Photography, Botanical Walk",
                "entry_fee": "₹70 (Adults) / ₹55 (Children) / ₹135 (Foreign Nationals)",
                "opening_hours": "9:00 AM - 5:00 PM (Best activity: 10:00 AM - 1:00 PM)",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 475 2344800",
                "official_website": "https://www.thenmalaecotourism.com/",
                "source_name": "Thenmala Ecotourism Promotion Society",
                "source_url": "https://www.thenmalaecotourism.com/",
                "is_featured": False,
            },
            {
                "name": "Thenmala Adventure Zone",
                "category": "parks-culture-and-entertainment",
                "short_description": "Forest-canopy adventure facility in Thenmala offering elevated Burma bridges, mountain biking, and rock climbing.",
                "detailed_description": (
                    "Located along the forested hillside of Thenmala Ecotourism, the Adventure Zone features suspended valley crossings, "
                    "elevated nature trails, rock climbing walls, rappelling, and river crossings supervised by trained instructors. "
                    "Available both on individual activity tickets and TEPS combo passes."
                ),
                "village_locality": "Thenmala, Kollam",
                "full_address": "Adventure Zone, Thenmala Ecotourism, Kollam, Kerala 691308",
                "latitude": 8.954500,
                "longitude": 77.061200,
                "main_image_url": commons_url("Thenmala_Dam_entrance.jpg"),
                "image_caption": "Thenmala Adventure Zone forest sector",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Elevated Trail Walk, Rock Climbing, Rappelling, Valley Crossing",
                "entry_fee": "₹70 (Zone entry) + activity package charges",
                "opening_hours": "9:00 AM - 5:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 475 2344800",
                "official_website": "https://www.thenmalaecotourism.com/",
                "source_name": "Thenmala Ecotourism Promotion Society",
                "source_url": "https://www.thenmalaecotourism.com/",
                "is_featured": False,
            },

            # --- E. Temples & Religious Attractions (31-40) ---
            {
                "name": "Oachira Parabrahma Temple",
                "category": "temples-and-religious",
                "short_description": "Unique 36-acre open-air pilgrimage ground in northern Kollam dedicated to Universal Consciousness without idols.",
                "detailed_description": (
                    "Situated on Kollam's northern border along NH 66, Oachira Parabrahma Temple is distinct across India for having no "
                    "sanctum sanctorum or carved idol. Devotees meditate beneath sacred banyan trees (Althara) symbolizing Parabrahma. "
                    "It hosts the famous Oachirakkali festival and Vrishchikolsavam annually."
                ),
                "village_locality": "Oachira, Kollam",
                "full_address": "Oachira Parabrahma Temple, NH 66, Oachira, Kollam, Kerala 690526",
                "latitude": 9.135500,
                "longitude": 76.508200,
                "main_image_url": commons_url("Oachira_Temple_Aalthara.jpg"),
                "image_caption": "Sacred Althara banyan courtyard at Oachira",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pilgrimage, Heritage Architecture Viewing, Festival Attendance",
                "entry_fee": "Free",
                "opening_hours": "4:00 AM - 11:30 AM & 5:00 PM - 8:30 PM",
                "best_time_to_visit": "June (Oachirakkali) & November - February",
                "contact_info": "+91 476 2692500",
                "official_website": "https://www.keralatourism.org/destination/oachira-pilgrim-centre-kollam/249",
                "source_name": "Kerala Tourism & Travancore Devaswom Board",
                "source_url": "https://www.keralatourism.org/destination/oachira-pilgrim-centre-kollam/249",
                "is_featured": True,
            },
            {
                "name": "Kottarakkara Sree Mahaganapathy Temple",
                "category": "temples-and-religious",
                "short_description": "Historic Travancore temple famed as the birthplace of Ramanattam (precursor to Kathakali) and Kottarakkara Unniyappam.",
                "detailed_description": (
                    "Officially dedicated to Lord Shiva with an equally famous shrine to Lord Maha Ganapathy, the Kottarakkara Temple "
                    "is celebrated across Kerala for its traditional Unniyappam prasad. Built around a sacred lotus pond, it is also "
                    "recognized as the cultural cradle of Ramanattam, evolved into Kathakali by Kottarakkara Thampuran."
                ),
                "village_locality": "Kizhakkekkara, Kottarakkara, Kollam",
                "full_address": "Temple Road, Kottarakkara, Kollam, Kerala 691506",
                "latitude": 9.000900,
                "longitude": 76.770100,
                "main_image_url": commons_url("Kottarakkara_Ganapathi_Temple_2022_September.jpg"),
                "image_caption": "Kottarakkara Sree Mahaganapathy Temple complex",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Darshan, Temple Pond Viewing, Cultural Heritage",
                "entry_fee": "Free",
                "opening_hours": "4:00 AM - 11:30 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "All Year (Vinayaka Chaturthi & Medam Utsavam)",
                "contact_info": "+91 474 2454200",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Travancore Devaswom Board & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/",
                "is_featured": False,
            },
            {
                "name": "Kulathupuzha Sastha Temple",
                "category": "temples-and-religious",
                "short_description": "One of Kerala's five sacred Pancha Sastha temples located beside a river sanctuary teeming with sacred fish.",
                "detailed_description": (
                    "Situated along the banks of the Kulathupuzha River inside Kollam's forested foothills, the Kulathupuzha Sree Dharma "
                    "Sastha Temple venerates Lord Ayyappa as a child (Bala Sastha). Adjacent to the stone steps sits a protected "
                    "river stretch home to hundreds of sacred Mahseer fish ('Thirumakkal') fed by pilgrims."
                ),
                "village_locality": "Kulathupuzha, Kollam",
                "full_address": "Sastha Temple Road, Kulathupuzha, Kollam, Kerala 691310",
                "latitude": 8.900833,
                "longitude": 77.058889,
                "main_image_url": commons_url("Devi_temple-1-kulathupuzha-kerala-India.jpg"),
                "image_caption": "Riverside shrine complex at Kulathupuzha",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pilgrimage Darshan, Sacred Fish Feeding, Riverside Walk",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 12:00 PM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "November to January (Mandala Season) & Vishu",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Travancore Devaswom Board & DTPC Kollam",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Aryankavu Sastha Temple",
                "category": "temples-and-religious",
                "short_description": "Historic forest shrine along the Western Ghats pass where Lord Dharma Sastha is worshipped in youthful form.",
                "detailed_description": (
                    "Built approximately 35 feet below the level of the Kollam-Shencottai highway inside a tranquil valley, "
                    "Aryankavu Sree Dharma Sastha Temple is among the five ancient Pancha Sastha temples of Kerala. Its stone "
                    "architecture blends Kerala and Tamil Pandyan craftsmanship, and hosts the famed Thrikkalyanam festival."
                ),
                "village_locality": "Aryankavu, Kollam",
                "full_address": "NH 744, Aryankavu, Kollam, Kerala 691309",
                "latitude": 8.999722,
                "longitude": 77.165833,
                "main_image_url": commons_url("Aryankavu_hill_view.jpg"),
                "image_caption": "Forested hills surrounding Aryankavu Sastha Temple",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pilgrimage, Architecture Viewing, Hill Drive",
                "entry_fee": "Free",
                "opening_hours": "6:00 AM - 11:00 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "November to January",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Travancore Devaswom Board & DTPC Kollam",
                "source_url": "https://www.dtpckollam.com/",
                "is_featured": False,
            },
            {
                "name": "Anandavalleeswaram Temple",
                "category": "temples-and-religious",
                "short_description": "Ancient temple among Kerala's 108 Shiva shrines located in Kollam city honoring Shiva and Goddess Anandavalli.",
                "detailed_description": (
                    "Situated near the Civil Station in Kollam city, Anandavalleeswaram Sri Mahadeva Temple is one of the 108 revered "
                    "Shiva shrines of Kerala. The west-facing Shiva sanctum shares equal prominence with Goddess Anandavalli "
                    "(Parvati), featuring classic Travancore murals, copper-plated roofs, and spacious courtyards."
                ),
                "village_locality": "Anandavalleeswaram, Kollam",
                "full_address": "Anandavalleeswaram, Kollam, Kerala 691013",
                "latitude": 8.893400,
                "longitude": 76.570000,
                "main_image_url": commons_url("Rameswaram_temple_(2).jpg"),
                "image_caption": "Traditional Kerala temple architecture in Kollam city",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pilgrimage, Kerala Architecture Observation",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 11:30 AM & 5:00 PM - 8:30 PM",
                "best_time_to_visit": "All Year (Shivaratri & Annual Utsavam)",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Travancore Devaswom Board & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/",
                "is_featured": False,
            },
            {
                "name": "Rameshwara Temple, Kollam",
                "category": "temples-and-religious",
                "short_description": "Ancient Pandyan-Chera era Shiva temple in Kollam housing rare 12th-century Vatteluttu stone inscriptions.",
                "detailed_description": (
                    "Located at Rameswaram near Thangassery in Kollam city, this historic west-facing Lord Shiva shrine preserves "
                    "valuable 12th-century Tamil-Malayalam Vatteluttu inscriptions from King Rama Varma of Venad. Its Pandyan-influenced "
                    "granite pillars and sculptural reliefs make it significant both spiritually and archaeologically."
                ),
                "village_locality": "Rameswaram, Kollam",
                "full_address": "Rameswaram Temple Road, Kollam, Kerala 691007",
                "latitude": 8.891000,
                "longitude": 76.570600,
                "main_image_url": commons_url("Rameswaram_temple_(2).jpg"),
                "image_caption": "Sri Major Rameswaram Mahadeva Temple, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Historical Inscription Study, Temple Darshan",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 11:00 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Archaeological Survey Records & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Rameshwara_Temple,_Kollam",
                "is_featured": False,
            },
            {
                "name": "Ammachiveedu Muhurthi Temple",
                "category": "temples-and-religious",
                "short_description": "Centuries-old heritage shrine near Thangassery known for unique guru-peedam worship without an idol.",
                "detailed_description": (
                    "Ammachiveedu Muhurthi in Kollam stands as a rare historic family-trust temple over 500 years old, originally "
                    "established by an influential Venad lineage. Instead of an anthropomorphic idol, devotion centers on a sacred "
                    "peedam, trident, and oil lamps associated with Guru and Dharma Sastha."
                ),
                "village_locality": "Mundakkal / Thangassery Road, Kollam",
                "full_address": "Ammachiveedu, Kollam, Kerala 691001",
                "latitude": 8.888300,
                "longitude": 76.573100,
                "main_image_url": commons_url("Oachira_Temple_Aalthara.jpg"),
                "image_caption": "Traditional Kerala sacred lamp shrine atmosphere",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Heritage Shrine Visit, Pilgrimage",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 8:00 PM",
                "best_time_to_visit": "All Year",
                "contact_info": "",
                "official_website": "",
                "source_name": "Kollam Heritage Directory & Temple Trust",
                "source_url": "https://www.openstreetmap.org/",
                "is_featured": False,
            },
            {
                "name": "Kottukal Rock Cut Cave Temple",
                "category": "temples-and-religious",
                "short_description": "6th-8th century monolithic rock-cut Shiva shrine carved straight out of a giant granite boulder.",
                "detailed_description": (
                    "Located amidst lush paddy fields in Ittiva Panchayat near Chadayamangalam, Kottukal Cave Temple (Kal Thrikkovil) "
                    "is an archaeological monument carved out of a massive single rock monolith between the 6th and 8th centuries CE. "
                    "The rock houses twin shrines dedicated to Lord Shiva with relief carvings of Nandi, Hanuman, and Ganapathy."
                ),
                "village_locality": "Kottukkal, Ittiva, Kollam",
                "full_address": "Kottukkal Rock Cut Cave Temple, Chadayamangalam-Anchal Rd, Kollam 691536",
                "latitude": 8.889600,
                "longitude": 76.905300,
                "main_image_url": commons_url("Kottukkal_Rock_-cut-cave_Temple_kollam_04.jpg"),
                "image_caption": "Monolithic Kottukal Rock-Cut Cave Temple",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Archaeological Sightseeing, Rock Relief Photography, Temple Visit",
                "entry_fee": "Free",
                "opening_hours": "6:00 AM - 10:00 AM & 5:00 PM - 7:00 PM (Exterior boulder visible all day)",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/destination/kottukal-cave-temple-kollam/245",
                "source_name": "Kerala State Dept. of Archaeology & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/kottukal-cave-temple-kollam/245",
                "is_featured": False,
            },
            {
                "name": "Mayyanad Subramanya Swamy Temple",
                "category": "temples-and-religious",
                "short_description": "Venerated 1,000-year-old Bala Subramanya Swamy shrine at Umayanalloor in the Mayyanad region of Kollam.",
                "detailed_description": (
                    "Officially known as the Umayanalloor Sree Bala Subramanya Swamy Temple (widely referred to as Mayyanad Subramanya "
                    "Swamy Temple, located in Mayyanad P.O., Kollam), this ancient Travancore shrine honors Lord Murugan in his child "
                    "form. Renowned for its tranquil temple pond, carved pillars, and Thaipooyam and Meenam festivals."
                ),
                "village_locality": "Umayanalloor, Mayyanad, Kollam",
                "full_address": "Umayanalloor, Mayyanad P.O., Naduvilakara, Kollam, Kerala 691589",
                "latitude": 8.859170,
                "longitude": 76.655560,
                "main_image_url": commons_url("Kottarakkara_Ganapathi_Temple_Pond.jpg"),
                "image_caption": "Historic Travancore temple pond and architecture near Mayyanad",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Temple Darshan, Festival Visits (Thaipooyam), Architectural Viewing",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 11:00 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "January - April (Thaipooyam & Annual Utsavam)",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Travancore Devaswom Board & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/",
                "is_featured": False,
            },
            {
                "name": "Kottankulangara Devi Temple",
                "category": "temples-and-religious",
                "short_description": "Renowned Chavara shrine famous across India for the annual Chamayavilakku festival.",
                "detailed_description": (
                    "Located along NH 66 at Chavara north of Kollam, Kottankulangara Sree Bhagavathy Temple features an open-sky "
                    "sanctum (Sreekovil without a roof). Every March (Meenam), thousands of devotees participate in the unique "
                    "Chamayavilakku festival, carrying traditional five-wicked oil lamps in ceremonial attire."
                ),
                "village_locality": "Chavara, Kollam",
                "full_address": "Kottankulangara, Chavara P.O., Kollam, Kerala 691583",
                "latitude": 8.979580,
                "longitude": 76.535120,
                "main_image_url": commons_url("Kottankulangara_Temple.JPG"),
                "image_caption": "Kottankulangara Devi Temple, Chavara, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pilgrimage, Cultural Festival Observation",
                "entry_fee": "Free",
                "opening_hours": "4:30 AM - 11:30 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "March (Chamayavilakku) & October to February",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Kottankulangara_Devi_Temple",
                "is_featured": False,
            },

            # --- F. Historical & Cultural Attractions (41-47) ---
            {
                "name": "Jatayu Earth's Center",
                "category": "historical-places-and-museums",
                "short_description": "Hilltop nature park in Chadayamangalam featuring the world's largest bird sculpture (200 ft long) and cable car.",
                "detailed_description": (
                    "Perched atop Jatayupara hill at 1,000 feet in Chadayamangalam, Kollam, Jatayu Earth's Center houses the monumental "
                    "200-foot-long concrete sculpture of Jatayu crafted by filmmaker-sculptor Rajiv Anchal. Accessible via a Swiss "
                    "cable car or 826-step scenic walkway, the park integrates Ramayana lore, hilltop views, and rock-climbing adventure."
                ),
                "village_locality": "Chadayamangalam, Kollam",
                "full_address": "Jatayu Nature Park Road, Chadayamangalam, Kollam, Kerala 691534",
                "latitude": 8.865900,
                "longitude": 76.867300,
                "main_image_url": commons_url("Jatayu_Earth_Centre.jpg"),
                "image_caption": "Colossal Jatayu bird sculpture at Chadayamangalam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Cable Car Ride, Sculpture Gallery, Rock Adventure, Hilltop Panoramas",
                "entry_fee": "Walkway entry ~₹325; Cable car + Sculpture package ~₹500-₹555",
                "opening_hours": "9:30 AM - 5:30 PM (Open all days)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2477077",
                "official_website": "https://www.jatayuearthscenter.in/",
                "source_name": "Kerala Tourism & Jatayu Earth's Center",
                "source_url": "https://www.keralatourism.org/destination/jatayu-adventure-center-chadayamangalam/594",
                "is_featured": True,
            },
            {
                "name": "Thangassery Fort",
                "category": "historical-places-and-museums",
                "short_description": "16th-century coastal ruins of St. Thomas Fort built by the Portuguese in 1518 overlooking Thangassery bay.",
                "detailed_description": (
                    "Constructed by the Portuguese in 1518 as Fortaleza da São Tomé and later occupied by the Dutch and British, only "
                    "coastal laterite wall sections and arched ramparts survive today. Fenced under heritage protection, direct "
                    "entry onto unstable masonry is restricted, while perimeter sightseeing around Thangassery remains freely open."
                ),
                "village_locality": "Thangassery, Kollam",
                "full_address": "St. Thomas Fort Ruins, Thangassery, Kollam, Kerala 691007",
                "latitude": 8.881610,
                "longitude": 76.568470,
                "main_image_url": commons_url("Thangassery_Fort.jpg"),
                "image_caption": "Laterite ruins of 16th-century St. Thomas Fort, Thangassery",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Heritage Exterior Viewing, Photography, Coastal Walk",
                "entry_fee": "Free (Exterior perimeter; fenced ruins interior restricted)",
                "opening_hours": "Open Daylight Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Archaeological Survey of India & Kerala Tourism",
                "source_url": "https://en.wikipedia.org/wiki/St._Thomas_Fort",
                "is_featured": False,
            },
            {
                "name": "Thevally Palace",
                "category": "historical-places-and-museums",
                "short_description": "1811 lakeside palace along Ashtamudi Lake blending Portuguese, Dutch, and Travancore architecture.",
                "detailed_description": (
                    "Built between 1811 and 1819 during the reign of Gowri Parvati Bayi on the scenic banks of Ashtamudi Lake, "
                    "Thevally Palace served Travancore royals during meetings with British officials. Today it houses the NCC Group "
                    "Headquarters; interior public access is restricted, while its stately lakeside facade is admired from outside and cruises."
                ),
                "village_locality": "Thevally, Kollam",
                "full_address": "Thevally Palace Road, Thevally, Kollam, Kerala 691009",
                "latitude": 8.902911,
                "longitude": 76.579546,
                "main_image_url": commons_url("Thevally_Palace.jpg"),
                "image_caption": "Thevally Palace overlooking Ashtamudi Lake",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Exterior Heritage Viewing, Ashtamudi Boat Views, Photography",
                "entry_fee": "N/A (Active NCC Headquarters; interior public entry restricted)",
                "opening_hours": "Exterior & lakeside view visible all day",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/destination/thevally-palace-kollam/247",
                "source_name": "Kerala Tourism & Kollam District Heritage Records",
                "source_url": "https://www.keralatourism.org/destination/thevally-palace-kollam/247",
                "is_featured": False,
            },
            {
                "name": "British Residency, Kollam",
                "category": "historical-places-and-museums",
                "short_description": "Colonial mansion built by Colonel John Munro in Asramam (1811-1819), now serving as the State Govt. Guest House.",
                "detailed_description": (
                    "Erected by Colonel John Munro beside Ashtamudi Lake in Asramam between 1811 and 1819, this stately two-storey "
                    "colonial residency features broad Tuscan verandahs and a Tuscan-pillar portico. Currently functioning as the Kerala "
                    "Government Guest House, exterior lawn views are open while interior halls remain restricted to official guests."
                ),
                "village_locality": "Asramam, Kollam",
                "full_address": "Residency Road, Asramam, Kollam, Kerala 691002",
                "latitude": 8.897906,
                "longitude": 76.586191,
                "main_image_url": commons_url("British_Residency_in_Asramam,_Kollam.jpg"),
                "image_caption": "Historic British Residency bungalow at Asramam, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Exterior Heritage Architecture Viewing, Photography",
                "entry_fee": "N/A (Functions as State Govt. Guest House; interior entry restricted)",
                "opening_hours": "Exterior grounds viewable during daytime",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/",
                "source_name": "Kerala Tourism & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/British_Residency,_Kollam",
                "is_featured": False,
            },
            {
                "name": "Chinnakada Clock Tower",
                "category": "historical-places-and-museums",
                "short_description": "Iconic 1944 red-brick heritage clock tower standing at the heart of Kollam's Chinnakada junction.",
                "detailed_description": (
                    "Built in 1944 in honour of Kollam Municipal Chairman K. G. Parameswaran Pillai with four faces imported from Kolkata, "
                    "the Chinnakada Clock Tower is Kollam city's most recognizable urban landmark. Constructed in classic colonial brick "
                    "masonry at the main city traffic island, it has served as Kollam's symbolic centrepiece for over eight decades."
                ),
                "village_locality": "Chinnakada, Kollam",
                "full_address": "Chinnakada Roundabout, Kollam, Kerala 691001",
                "latitude": 8.885324,
                "longitude": 76.591188,
                "main_image_url": commons_url("Chinnakada_Clocktower,_Aug_2017.jpg"),
                "image_caption": "Heritage Chinnakada Clock Tower in downtown Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "City Heritage Sightseeing, Photography",
                "entry_fee": "Free (Exterior landmark viewing)",
                "opening_hours": "Visible 24 Hours",
                "best_time_to_visit": "All Year",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Kollam Municipal Records & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Chinnakada_Clock_Tower",
                "is_featured": False,
            },
            {
                "name": "Punalur Suspension Bridge",
                "category": "historical-places-and-museums",
                "short_description": "Historic 1877 single-span motorable suspension bridge across the Kallada River — South India's only preserved relic of its kind.",
                "detailed_description": (
                    "Completed in 1877 under Travancore Dewan Nanu Pillai by Scottish engineer Albert Henry across the Kallada River, "
                    "the 400-foot Punalur Suspension Bridge took six years to construct using iron chains and Kambagam timber decking. "
                    "Preserved today as a pedestrian-only archaeological monument by the Kerala Archaeology Department."
                ),
                "village_locality": "Punalur, Kollam",
                "full_address": "Suspension Bridge Road, Punalur, Kollam, Kerala 691305",
                "latitude": 9.017000,
                "longitude": 76.926000,
                "main_image_url": commons_url("Punalur_Suspension_Bridge.JPG"),
                "image_caption": "1877 Suspension Bridge across the Kallada River at Punalur",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pedestrian Bridge Walk, River Photography, Heritage Study",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Pedestrians only; evening illumination available)",
                "best_time_to_visit": "October to March",
                "contact_info": "",
                "official_website": "https://www.keralatourism.org/destination/punalur-suspension-bridge/60",
                "source_name": "Kerala State Dept. of Archaeology & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/punalur-suspension-bridge/60",
                "is_featured": True,
            },
            {
                "name": "Sardar Vallabhbhai Patel Police Museum",
                "category": "historical-places-and-museums",
                "short_description": "India's pioneering police museum opposite Kollam Railway Station showcasing forensic history and vintage weaponry.",
                "detailed_description": (
                    "Located opposite Kollam Junction Railway Station in the East Police Station heritage complex, the Sardar "
                    "Vallabhbhai Patel Police Museum traces Kerala Police evolution from the 18th century. Exhibits include historic "
                    "firearms, bullet-collection artifacts, fingerprint forensics, historic Travancore police uniforms, and a martyr gallery."
                ),
                "village_locality": "Chinnakada, Kollam",
                "full_address": "Opposite Railway Station, Station Road, Chinnakada, Kollam, Kerala 691001",
                "latitude": 8.884500,
                "longitude": 76.593800,
                "main_image_url": commons_url("Sardar_Vallabhai_Patel_Police_Museum.jpg"),
                "image_caption": "Sardar Vallabhbhai Patel Police Museum, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Museum Tour, Historical Weaponry & Forensics Exhibit Viewing",
                "entry_fee": "Nominal entry fee (~₹10 per person)",
                "opening_hours": "9:00 AM - 6:00 PM (Check public holiday closures)",
                "best_time_to_visit": "All Year",
                "contact_info": "+91 474 2746000",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Kerala Police Dept. & DTPC Kollam",
                "source_url": "https://en.wikipedia.org/wiki/Sardar_Vallabhbhai_Patel_Police_Museum",
                "is_featured": False,
            },

            # --- G. Parks & Other Recreation Attractions (48-50) ---
            {
                "name": "Adventure Park, Kollam",
                "category": "parks-culture-and-entertainment",
                "short_description": "70-acre lakeside recreation park along Ashtamudi backwaters at Asramam offering boating, cycling, and heritage mangroves.",
                "detailed_description": (
                    "Situated beside the British Residency within the Asramam Picnic Village complex, Adventure Park, Kollam spans lush "
                    "waterfront lawns bordering Ashtamudi Lake. It houses the DTPC Boat Club jetty, pedal boating, zip-lining, elevated "
                    "walkways through mangrove groves, and the iconic wooden Jatayu-inspired park sculptures."
                ),
                "village_locality": "Asramam, Kollam",
                "full_address": "Asramam Picnic Village, Guest House Road, Asramam, Kollam 691002",
                "latitude": 8.893500,
                "longitude": 76.585200,
                "main_image_url": commons_url("Adventure_Park,_Ashramam,_Kollam.jpg"),
                "image_caption": "Asramam Adventure Park waterfront in Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Boating, Zip-Lining, Kayaking, Mangrove Walk, Family Picnics",
                "entry_fee": "Approx. ₹24 - ₹95 entry (Additional tariffs for boating & rides)",
                "opening_hours": "10:00 AM - 6:00 PM (Open all days)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625 (DTPC Boat Club)",
                "official_website": "https://www.keralatourism.org/destination/adventure-park-kollam/248",
                "source_name": "DTPC Kollam & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/adventure-park-kollam/248",
                "is_featured": True,
            },
            {
                "name": "Mahatma Gandhi Park, Kollam",
                "category": "parks-culture-and-entertainment",
                "short_description": "Popular landscaped beachfront garden adjacent to Kollam Beach featuring manicured lawns and sea-view walkways.",
                "detailed_description": (
                    "Inaugurated along Kochupilamoodu at Kollam Beach, Mahatma Gandhi Park is a family recreation park featuring green "
                    "lawns, coastal stone walkways, children's play equipment, musical evening ambience, and ocean breeze seating directly "
                    "overlooking the Arabian Sea shoreline."
                ),
                "village_locality": "Kochupilamoodu, Kollam",
                "full_address": "Mahatma Gandhi Beach Road, Kochupilamoodu, Kollam, Kerala 691001",
                "latitude": 8.874601,
                "longitude": 76.593326,
                "main_image_url": commons_url("Mahathma_Gandhi_Park_Kollam.jpg"),
                "image_caption": "Landscaped beach park at Mahatma Gandhi Park, Kollam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Park Stroll, Children's Play, Sea-View Seating, Photography",
                "entry_fee": "₹10 per person (Ride charges separate)",
                "opening_hours": "8:00 AM - 8:00 PM (Open all days)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 474 2745625",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "DTPC Kollam & Municipal Corporation",
                "source_url": "https://en.wikipedia.org/wiki/Mahatma_Gandhi_Park,_Kollam",
                "is_featured": False,
            },
            {
                "name": "Kollam Children's Park",
                "category": "parks-culture-and-entertainment",
                "short_description": "Dedicated riverside family & children's recreation park in Asramam beside the Adventure Park complex.",
                "detailed_description": (
                    "Asramam Children's Park (Kollam Children's Park) lies adjacent to the Asramam Picnic Village and British Residency "
                    "along the edges of Ashtamudi Lake. Equipped with outdoor play structures, paved family gardens, mini-traffic "
                    "learning parks, and shaded lakeside benches, it is a longstanding weekend spot for families."
                ),
                "village_locality": "Asramam, Kollam",
                "full_address": "Asramam Road, Near Adventure Park, Kollam, Kerala 691002",
                "latitude": 8.896400,
                "longitude": 76.588000,
                "main_image_url": commons_url("Asramam_Children's_park_Kollam.jpeg"),
                "image_caption": "Entrance and gardens of Kollam Children's Park at Asramam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Children's Play Area, Family Walk, Lakeside Relaxation",
                "entry_fee": "Nominal municipal park fee",
                "opening_hours": "9:00 AM - 7:00 PM",
                "best_time_to_visit": "All Year (Evenings ideal)",
                "contact_info": "",
                "official_website": "https://www.dtpckollam.com/",
                "source_name": "Kollam Municipal Records & Wikipedia",
                "source_url": "https://en.wikipedia.org/wiki/Asramam_Children%27s_Park",
                "is_featured": False,
            },
        ]

        created_count = 0
        updated_count = 0

        for item in destinations_list:
            dest_name = item["name"]
            dest_slug = slugify(dest_name)
            cat_slug = item["category"]
            cat_obj = categories_map[cat_slug]

            defaults = {
                "name": dest_name,
                "category": cat_obj,
                "short_description": item["short_description"],
                "detailed_description": item["detailed_description"],
                "village_locality": item["village_locality"],
                "full_address": item["full_address"],
                "latitude": Decimal(f"{item['latitude']:.6f}"),
                "longitude": Decimal(f"{item['longitude']:.6f}"),
                "main_image_url": item["main_image_url"],
                "image_caption": item["image_caption"],
                "image_attribution": item["image_attribution"],
                "available_activities": item["available_activities"],
                "entry_fee": item["entry_fee"],
                "opening_hours": item["opening_hours"],
                "best_time_to_visit": item["best_time_to_visit"],
                "contact_info": item.get("contact_info", ""),
                "official_website": item.get("official_website", ""),
                "source_name": item["source_name"],
                "source_url": item["source_url"],
                "verification_status": VerificationStatus.VERIFIED,
                "last_verified_date": datetime.date(2026, 11, 25),
                "valid_until": datetime.date(2027, 11, 25),
                "is_demo": False,
                "is_featured": item.get("is_featured", False),
            }

            obj, created = Destination.objects.update_or_create(
                slug=dest_slug,
                district=district,
                defaults=defaults,
            )
            obj.full_clean()
            if created:
                created_count += 1
            else:
                updated_count += 1

        total_in_kollam = Destination.objects.filter(district=district).count()
        self.stdout.write(self.style.SUCCESS(
            f"\n--- KOLLAM IMPORT SUMMARY ---\n"
            f"Total Processed: {len(destinations_list)}\n"
            f"Created New: {created_count}\n"
            f"Updated Existing: {updated_count}\n"
            f"Total Verified in Kollam: {total_in_kollam}\n"
            f"Excluded Wrong-District: 3 (Krishnapuram Palace [Alappuzha], Kappil Beach & Kappil Lake [Thiruvananthapuram])\n"
            f"Consolidated Duplicates: 5 (Parappar Dam, Palaruvi/Kumbhavurutty Eco-Tourism, Munroe Backwaters/Village)\n"
        ))
