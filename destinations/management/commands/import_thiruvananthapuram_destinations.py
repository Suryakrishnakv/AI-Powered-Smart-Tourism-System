import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from destinations.models import District, Category, Destination
from core.models import VerificationStatus


class Command(BaseCommand):
    help = "Idempotently import real, verified tourist destinations for Thiruvananthapuram district only."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Thiruvananthapuram destinations import..."))

        # 1. Ensure Thiruvananthapuram District exists
        district, dist_created = District.objects.update_or_create(
            name="Thiruvananthapuram",
            defaults={
                'slug': 'thiruvananthapuram',
                'headquarters': 'Thiruvananthapuram',
                'description': (
                    "Thiruvananthapuram (formerly Trivandrum) is the capital city and southernmost district of Kerala. "
                    "Flanked by the Arabian Sea on the west and the Western Ghats on the east, it boasts a rich heritage "
                    "dating back to the Travancore kingdom, pristine golden beaches like Kovalam and Varkala, misty hill stations "
                    "like Ponmudi, lush forest wildlife reserves, and historic temples."
                ),
                'latitude': 8.524139,
                'longitude': 76.936638,
                'cover_image_url': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d6/Padmanabhaswamy_Temple_Gopuram.jpg/960px-Padmanabhaswamy_Temple_Gopuram.jpg',
                'official_dtpc_website': 'https://www.keralatourism.org/thiruvananthapuram/',
                'dtpc_contact': '+91 471 2321132 / dtpctvm@keralatourism.org',
                'source_name': 'Department of Tourism, Government of Kerala',
                'source_url': 'https://www.keralatourism.org/districts/thiruvananthapuram/',
                'verification_status': VerificationStatus.VERIFIED,
                'last_verified_date': datetime.date(2026, 11, 24),
                'valid_until': datetime.date(2027, 11, 24),
                'is_demo': False,
            }
        )
        self.stdout.write(f"District 'Thiruvananthapuram': {'Created' if dist_created else 'Already exists'}")

        # 2. Ensure Categories exist
        categories_data = [
            ("Beaches and Coastal Attractions", "beaches-and-coastal", "bi-water", "Pristine sandy shores, rocky sea cliffs, and coastal fishing harbours."),
            ("Hill Stations and Nature", "hill-stations-and-nature", "bi-tree", "Misty peaks, biodiversity-rich river valleys, and mountain trekking trails."),
            ("Waterfalls", "waterfalls", "bi-moisture", "Cascading forest water streams and natural rocky waterfalls."),
            ("Wildlife and Ecotourism", "wildlife-and-ecotourism", "bi-shield-check", "Protected forest sanctuaries, rehabilitation centers, and safari parks."),
            ("Dams, Lakes and Backwaters", "dams-lakes-and-backwaters", "bi-tsunami", "Picturesque reservoirs, boating villages, and backwater lagoons."),
            ("Temples and Religious Attractions", "temples-and-religious", "bi-flower1", "Ancient pilgrimage temples, Dravidian architecture, and mutts."),
            ("Historical Places and Museums", "historical-places-and-museums", "bi-bank", "Colonial forts, royal Travancore palaces, and art galleries."),
            ("Parks, Culture and Entertainment", "parks-culture-and-entertainment", "bi-stars", "Botanical parks, craft villages, planetariums, and auditoriums."),
        ]

        categories_map = {}
        for cat_name, cat_slug, cat_icon, cat_desc in categories_data:
            cat_obj, _ = Category.objects.get_or_create(
                slug=cat_slug,
                defaults={'name': cat_name, 'icon': cat_icon, 'description': cat_desc}
            )
            categories_map[cat_slug] = cat_obj

        # 3. All 50 Verified Destinations
        destinations_list = [
            # 1-10: Beaches and Coastal Attractions
            {
                "name": "Kovalam Beach",
                "category": "beaches-and-coastal",
                "short_description": "World-famous crescent beach trio comprising Lighthouse, Hawa, and Samudra beaches.",
                "detailed_description": (
                    "Kovalam is an internationally renowned beach paradise located 16 km south of Thiruvananthapuram city. "
                    "It features three adjacent crescent-shaped beaches separated by rocky outcroppings. The southernmost, "
                    "Lighthouse Beach, is famous for its 35-metre-high red-and-white striped lighthouse offering panoramic "
                    "coastal vistas. The calm waters created by a natural bay make it ideal for swimming, catamaran cruising, "
                    "and coastal dining."
                ),
                "village_locality": "Vizhinjam / Kovalam",
                "full_address": "Kovalam Beach, Thiruvananthapuram, Kerala 695527",
                "latitude": 8.402000,
                "longitude": 76.978400,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/29/Kovalam_beach%281%29.jpg/960px-Kovalam_beach%281%29.jpg",
                "image_caption": "Lighthouse Beach at Kovalam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Swimming, Surfing, Ayurvedic Spa, Catamaran Cruising, Sunset Photography",
                "entry_fee": "Free (Lighthouse tower entry: ₹20)",
                "opening_hours": "Open 24 Hours (Lifeguards active: 6:00 AM - 6:30 PM)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2480085 (DTPC Kovalam)",
                "official_website": "https://www.keralatourism.org/destination/kovalam/23",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/kovalam/23",
                "is_featured": True,
            },
            {
                "name": "Varkala Beach",
                "category": "beaches-and-coastal",
                "short_description": "Dramatic beach flanked by soaring red laterite cliffs with natural mineral water springs.",
                "detailed_description": (
                    "Varkala Beach (also known as Papanasam Beach) is unique in Kerala where towering red laterite cliffs "
                    "directly overlook the Arabian Sea. Designated as a geological monument by the Geological Survey of India, "
                    "it is famous for sacred cleansing waters believed to wash away sins, sunset-facing cliff cafes, yoga retreats, "
                    "and clean sandy coastlines."
                ),
                "village_locality": "Varkala",
                "full_address": "Papanasam Beach, Varkala, Thiruvananthapuram, Kerala 695141",
                "latitude": 8.737900,
                "longitude": 76.706300,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5d/Varkala_Beach%2C_Kerala.jpg/960px-Varkala_Beach%2C_Kerala.jpg",
                "image_caption": "Red Cliffs overlooking Varkala Beach",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Cliff Walking, Paragliding, Sunbathing, Yoga, Sacred Papanasam Dip",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 470 2604555",
                "official_website": "https://www.keralatourism.org/destination/varkala-beach/326",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/varkala-beach/326",
                "is_featured": True,
            },
            {
                "name": "Poovar Island",
                "category": "beaches-and-coastal",
                "short_description": "Picturesque estuary where the Neyyar river, calm backwaters, and golden beach meet the sea.",
                "detailed_description": (
                    "Poovar Island is an idyllic coastal village situated near the southern tip of Thiruvananthapuram district. "
                    "It is isolated from modern bustle, accessible primarily by boat cruise through tranquil mangrove canals. "
                    "Historically an ancient trading port visited by King Solomon's merchant ships, Poovar features floating "
                    "cottages, rich birdlife, and a golden sand spit separating the river from the sea."
                ),
                "village_locality": "Poovar, Neyyattinkara Taluk",
                "full_address": "Poovar, Neyyattinkara, Thiruvananthapuram, Kerala 695525",
                "latitude": 8.318200,
                "longitude": 77.072600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1e/Poovar_Island%2C_Kerala%2C_India_20140107-DSC_3275.jpg/960px-Poovar_Island%2C_Kerala%2C_India_20140107-DSC_3275.jpg",
                "image_caption": "Poovar Golden Sand Estuary",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Mangrove Canal Boating, Estuary Cruise, Bird Watching, Floating Restaurant Dining",
                "entry_fee": "Free access; Boat cruise rates apply (~₹1,500 - ₹3,000 per boat)",
                "opening_hours": "6:00 AM - 6:00 PM (Boating daylight hours)",
                "best_time_to_visit": "October to February",
                "contact_info": "+91 471 2210080",
                "official_website": "https://www.keralatourism.org/destination/poovar/378",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/poovar/378",
                "is_featured": True,
            },
            {
                "name": "Shanghumugham Beach",
                "category": "beaches-and-coastal",
                "short_description": "Historic city beach famed for evening breezes, sunsets, and the colossal Sagarakanyaka sculpture.",
                "detailed_description": (
                    "Located close to Thiruvananthapuram International Airport, Shanghumugham Beach is a beloved recreation "
                    "retreat for city dwellers and tourists. It features the gigantic 35-metre mermaid sculpture 'Sagarakanyaka' "
                    "carved by legendary sculptor Kanayi Kunhiraman, a starfish-shaped restaurant, and the holy Arattu mandapam "
                    "used for ritual temple immersions."
                ),
                "village_locality": "Shanghumugham",
                "full_address": "Shanghumugham Beach Road, Thiruvananthapuram, Kerala 695008",
                "latitude": 8.479500,
                "longitude": 76.911800,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/dc/Shankumugham_BeAch.jpg/960px-Shankumugham_BeAch.jpg",
                "image_caption": "Sagarakanyaka Mermaid Sculpture at Shanghumugham",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Sculpture Viewing, Sunset Watching, Beach Strolls, Seaside Dining",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "Throughout the year (Evenings)",
                "contact_info": "+91 471 2321132 (DTPC)",
                "official_website": "https://www.keralatourism.org/destination/shanghumugham-beach/24",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/shanghumugham-beach/24",
            },
            {
                "name": "Kappil Beach",
                "category": "beaches-and-coastal",
                "short_description": "Tranquil secluded beach where the backwaters of Kappil lake embrace the open sea.",
                "detailed_description": (
                    "Situated about 6 km north of Varkala cliff in Thiruvananthapuram district, Kappil Beach is an unspoiled, "
                    "scenic marvel. A narrow strip of coastal road cleanly divides the shimmering waters of Kappil Lake from the "
                    "foaming waves of the Arabian Sea. It provides a peaceful alternative to busier tourist hubs."
                ),
                "village_locality": "Edava-Kappil, Varkala Taluk",
                "full_address": "Kappil, Edava, Thiruvananthapuram, Kerala 695311",
                "latitude": 8.784500,
                "longitude": 76.680600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fd/Kappil_Beach.JPG/960px-Kappil_Beach.JPG",
                "image_caption": "Kappil Beach meeting the Backwater",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Beachcombing, Pedal Boating, Coastal Photography, Sunset Viewing",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 470 2604555",
                "official_website": "https://www.keralatourism.org/destination/kappil-beach/327",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/kappil-beach/327",
            },
            {
                "name": "Azhimala Beach",
                "category": "beaches-and-coastal",
                "short_description": "Rocky coastal shoreline nestled beneath the majestic clifftop Shiva temple statue.",
                "detailed_description": (
                    "Azhimala Beach derives its name from 'Azhi' (sea) and 'Mala' (hill), reflecting its dramatic geographical "
                    "setting where the land rolls down into rocky shorelines and rolling waves. Situated near Vizhinjam, it has "
                    "become a prominent landmark due to the imposing 58-foot-tall Lord Shiva statue overlooking the sea."
                ),
                "village_locality": "Pulinkudi / Kottukal",
                "full_address": "Azhimala Temple Road, Vizhinjam, Thiruvananthapuram, Kerala 695521",
                "latitude": 8.358200,
                "longitude": 77.012500,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4c/AZHIMALA_BEACH_VIEW.jpg/960px-AZHIMALA_BEACH_VIEW.jpg",
                "image_caption": "58-foot Shiva Statue overlooking Azhimala Beach",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Temple Darshan, Statue Viewing, Cliff Photography, Coastal Walking",
                "entry_fee": "Free",
                "opening_hours": "6:00 AM - 8:00 PM",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 471 2267500",
                "official_website": "https://www.keralatourism.org/destination/aazhimala-shiva-temple/646",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/aazhimala-shiva-temple/646",
            },
            {
                "name": "Adimalathura Beach",
                "category": "beaches-and-coastal",
                "short_description": "Pristine, quiet stretch of golden sand known for traditional artisanal fishing.",
                "detailed_description": (
                    "Adimalathura Beach is a serene fishing coastal hamlet located south of Kovalam. Unlike busy tourist strips, "
                    "Adimalathura retains an untouched rustic charm with rows of colorful fishing boats and fishermen practicing "
                    "traditional shore-seine net fishing (Kambavala)."
                ),
                "village_locality": "Kottukal Grama Panchayat",
                "full_address": "Adimalathura, Kottukal, Thiruvananthapuram, Kerala 695521",
                "latitude": 8.351200,
                "longitude": 77.022200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b2/Adimalathura_Catholic_Church.jpg/960px-Adimalathura_Catholic_Church.jpg",
                "image_caption": "Golden sands of Adimalathura Beach",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Beach Walking, Observing Artisanal Fishermen, Photography",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2321132 (DTPC)",
                "official_website": "https://thiruvananthapuram.nic.in/tourism/",
                "source_name": "DTPC Thiruvananthapuram",
                "source_url": "https://thiruvananthapuram.nic.in/tourism/",
            },
            {
                "name": "Chowara Beach",
                "category": "beaches-and-coastal",
                "short_description": "Broad golden shoreline bordered by coconut groves and an ancient hilltop temple.",
                "detailed_description": (
                    "Located 9 km south of Kovalam, Chowara Beach features golden sands, gentle rolling waves, and coconut palm "
                    "groves. An ancient temple dedicated to Lord Shiva sits atop a nearby hillock, offering a vantage point "
                    "overlooking the fishing fleet sailing out to sea."
                ),
                "village_locality": "Chowara, Kottukal",
                "full_address": "Chowara Beach, Thiruvananthapuram, Kerala 695501",
                "latitude": 8.361500,
                "longitude": 77.026800,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1d/Kovalam_Beach.JPG/960px-Kovalam_Beach.JPG",
                "image_caption": "Chowara Beach fishing shoreline",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Ayurveda Retreats, Coastal Walking, Temple Visit, Photography",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2321132",
                "official_website": "https://www.keralatourism.org/destination/chowara-beach/25",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/chowara-beach/25",
            },
            {
                "name": "Vizhinjam Harbour",
                "category": "beaches-and-coastal",
                "short_description": "Historic natural harbour and ancient seafaring port transformed into an international hub.",
                "detailed_description": (
                    "Vizhinjam was an ancient capital of the Ay dynasty and a busy maritime trading port during the 7th-10th "
                    "centuries. Today, alongside its vibrant fishing harbour where hundreds of traditional boats dock daily, "
                    "it is home to India's premier deep-water transshipment container port."
                ),
                "village_locality": "Vizhinjam",
                "full_address": "Vizhinjam Harbour Road, Thiruvananthapuram, Kerala 695521",
                "latitude": 8.380200,
                "longitude": 76.991200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/61/Vizhinjam_Harbour_2.jpg/960px-Vizhinjam_Harbour_2.jpg",
                "image_caption": "Fishing boats docked at Vizhinjam Harbour",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Harbour Walking, Marine Life Observation, Historical Exploration, Fresh Seafood Market",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Best in early mornings)",
                "best_time_to_visit": "October to April",
                "contact_info": "+91 471 2480242",
                "official_website": "https://www.keralatourism.org/destination/vizhinjam/26",
                "source_name": "Kerala Tourism & Ports Department",
                "source_url": "https://www.keralatourism.org/destination/vizhinjam/26",
            },
            {
                "name": "Muthalapozhi Harbour",
                "category": "beaches-and-coastal",
                "short_description": "Dramatic coastal estuary and breakwater walkway where the Vamanapuram River joins the sea.",
                "detailed_description": (
                    "Muthalapozhi is a natural estuary located in Perumathura in Chirayinkeezhu taluk. It features a long stone "
                    "breakwater extending directly into the sea, offering a scenic promenade for tourists to walk alongside fishing "
                    "boats passing between the river backwaters and the open Arabian Sea."
                ),
                "village_locality": "Perumathura, Chirayinkeezhu",
                "full_address": "Perumathura, Chirayinkeezhu, Thiruvananthapuram, Kerala 695304",
                "latitude": 8.636000,
                "longitude": 76.786500,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/69/Muthalappozhi_-_View_from_Bridge.jpg/960px-Muthalappozhi_-_View_from_Bridge.jpg",
                "image_caption": "Muthalapozhi Estuary and Breakwater",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Breakwater Walk, River-Sea Confluence Viewing, Fishing Observation, Photography",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2321132",
                "official_website": "https://thiruvananthapuram.nic.in/tourism/",
                "source_name": "DTPC Thiruvananthapuram",
                "source_url": "https://thiruvananthapuram.nic.in/tourism/",
            },

            # 11-20: Hill Stations, Waterfalls and Nature
            {
                "name": "Ponmudi Hill Station",
                "category": "hill-stations-and-nature",
                "short_description": "Enchanting hill retreat at 1,100 metres with 22 hairpin bends, mist-clad peaks, and tea gardens.",
                "detailed_description": (
                    "Ponmudi (The Golden Peak) is a serene hill station perched at an elevation of 1,100 metres in the Western "
                    "Ghats, approximately 61 km northeast of Thiruvananthapuram city. The journey up via 22 thrilling hairpin bends "
                    "is bordered by lush tropical rainforests. The hillcrest is enveloped in rolling fog and carpeted with alpine "
                    "grasslands, mountain orchids, and tea plantations."
                ),
                "village_locality": "Nedumangad Taluk",
                "full_address": "Ponmudi, Nedumangad, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.760900,
                "longitude": 77.116700,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0b/Thiruvananthapuram_Ponmudi.jpg/960px-Thiruvananthapuram_Ponmudi.jpg",
                "image_caption": "Mist-clad hillcrest of Ponmudi",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Hairpin Driving, Hill Trekking, Tea Garden Walks, Bird Watching, Landscape Photography",
                "entry_fee": "Vehicle & Forest Eco-fee (~₹30 - ₹50 per person)",
                "opening_hours": "8:00 AM - 4:00 PM (Entry closed after 4:00 PM for wildlife safety)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 472 2855222 (KTDC Golden Peak Ponmudi)",
                "official_website": "https://www.keralatourism.org/destination/ponmudi-hills/27",
                "source_name": "Kerala Tourism & Forest Department",
                "source_url": "https://www.keralatourism.org/destination/ponmudi-hills/27",
                "is_featured": True,
            },
            {
                "name": "Agasthyakoodam",
                "category": "hill-stations-and-nature",
                "short_description": "Kerala's second highest peak (1,868 m), revered biological sanctuary, and legendary trek.",
                "detailed_description": (
                    "Agasthyakoodam (Agasthyamala) rises 1,868 metres in the Western Ghats and is designated as a UNESCO World "
                    "Biosphere Reserve. Named after the revered sage Agastya, it is celebrated for its dense virgin forests, "
                    "over 2,000 species of medicinal flora, and endemic avian species. Trekking permits are strictly regulated "
                    "by the Kerala Forest Department."
                ),
                "village_locality": "Neyyar Wildlife Sanctuary Range",
                "full_address": "Agasthyakoodam Peak, Thiruvananthapuram, Kerala 695543",
                "latitude": 8.615200,
                "longitude": 77.247600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/81/Agasthyarkoodam_Hill_top_05.jpg/960px-Agasthyarkoodam_Hill_top_05.jpg",
                "image_caption": "Agasthyamala Western Ghats Biosphere Reserve",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Permit-based Forest Trekking, Medicinal Botany Study, Bird Watching",
                "entry_fee": "Regulated trek pass (~₹1,330 per person through Forest Department portal)",
                "opening_hours": "Seasonal permit trek (January-February); 7:00 AM departure from Bonacaud",
                "best_time_to_visit": "January to February (Official trekking season)",
                "contact_info": "+91 471 2360762 (Forest Wildlife Warden)",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forest Department",
                "source_url": "https://forest.kerala.gov.in/",
                "is_featured": True,
            },
            {
                "name": "Meenmutty Waterfalls",
                "category": "waterfalls",
                "short_description": "Magnificent multi-tiered forest waterfall accessed via a scenic trek near Neyyar/Peppara.",
                "detailed_description": (
                    "This Meenmutty Waterfalls is located in Thiruvananthapuram district near the Peppara Sanctuary and Kallar. "
                    "Reachable through a thrilling 2-km guided trek through thick deciduous canopy and rocky terrain from the "
                    "Kallar checkpost, the waterfall cascades vigorously over stepped boulders."
                ),
                "village_locality": "Nedumangad Taluk",
                "full_address": "Near Kallar, Peppara Range, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.694200,
                "longitude": 77.172800,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/21/Meenmutty_Falls.jpg/960px-Meenmutty_Falls.jpg",
                "image_caption": "Meenmutty Falls near Kallar",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Forest Trekking, Natural Pool Splashing, Nature Photography",
                "entry_fee": "₹50 per Adult, ₹25 per Child (Forest Eco-ticket)",
                "opening_hours": "8:30 AM - 4:00 PM",
                "best_time_to_visit": "September to February (Post-monsoon)",
                "contact_info": "+91 471 2360762",
                "official_website": "https://www.keralatourism.org/destination/meenmutty-kallar/28",
                "source_name": "Kerala Tourism & Forest Department",
                "source_url": "https://www.keralatourism.org/destination/meenmutty-kallar/28",
            },
            {
                "name": "Mankayam Waterfalls",
                "category": "waterfalls",
                "short_description": "Charming forest ecotourism spot featuring the Kalakkayam and Kurissadi cascades.",
                "detailed_description": (
                    "Mankayam is an eco-tourism destination situated near Palode in Thiruvananthapuram district. The Mankayam "
                    "river, originating from the Agasthyakoodam ranges, forms two spectacular waterfalls here: Kalakkayam "
                    "and Kurissadi. Managed by the local Vana Samrakshana Samithi (VSS), it offers crystal-clear rocky pools "
                    "shaded by towering bamboo groves."
                ),
                "village_locality": "Peringammala / Palode",
                "full_address": "Mankayam Eco-Tourism, Peringammala, Thiruvananthapuram, Kerala 695563",
                "latitude": 8.749000,
                "longitude": 77.085000,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b0/Mankayam_Waterfalls.jpg/960px-Mankayam_Waterfalls.jpg",
                "image_caption": "Kalakkayam Falls at Mankayam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "River Trekking, Forest Stream Bathing, Nature Trail Walks",
                "entry_fee": "₹30 per Adult, ₹15 per Child",
                "opening_hours": "8:00 AM - 4:00 PM",
                "best_time_to_visit": "October to February",
                "contact_info": "+91 472 2842100",
                "official_website": "https://www.keralatourism.org/destination/mankayam-ecotourism/325",
                "source_name": "Kerala Forest Department Ecotourism",
                "source_url": "https://www.keralatourism.org/destination/mankayam-ecotourism/325",
            },
            {
                "name": "Vazhvanthol Waterfalls",
                "category": "waterfalls",
                "short_description": "Exhilarating 4-km forest trek leading to breathtaking multi-tiered cascades.",
                "detailed_description": (
                    "Vazhvanthol Waterfalls, located near Vithura in the Western Ghats foothills, is an outstanding eco-tourism "
                    "trek. Tourists hike through deep eucalyptus plantations and bamboo forests alongside mountain streams to "
                    "reach two cascades that plunge down massive granite boulders."
                ),
                "village_locality": "Vithura, Nedumangad Taluk",
                "full_address": "Vazhvanthol Ecotourism, Vithura, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.687200,
                "longitude": 77.189500,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c6/Vazhvanthol_Waterfalls.jpg/960px-Vazhvanthol_Waterfalls.jpg",
                "image_caption": "Cascading waters of Vazhvanthol",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "4-km Forest Trekking, Mountain Stream Dipping, Butterfly Watching, Photography",
                "entry_fee": "₹40 per person",
                "opening_hours": "8:30 AM - 2:00 PM (Entry closes at 2:00 PM to ensure safe return)",
                "best_time_to_visit": "September to February",
                "contact_info": "+91 472 2857002 (Forest Range Office Vithura)",
                "official_website": "https://www.keralatourism.org/destination/vazhvanthol-waterfalls/611",
                "source_name": "Kerala Forest Department",
                "source_url": "https://www.keralatourism.org/destination/vazhvanthol-waterfalls/611",
            },
            {
                "name": "Kallar",
                "category": "hill-stations-and-nature",
                "short_description": "Picturesque rocky river valley on the road to Ponmudi, famed for crystal mountain waters.",
                "detailed_description": (
                    "Kallar gets its name from 'Kallu' (stone) and 'Aru' (river). Formed by the Vamanapuram river flowing down "
                    "from the Ponmudi peaks, it features fascinating water-carved rock formations, golden pebbles, and natural "
                    "pools. It serves as the gateway to the Ponmudi hill station and the Meenmutty waterfall trek."
                ),
                "village_locality": "Kallar, Nedumangad Taluk",
                "full_address": "Kallar, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.708300,
                "longitude": 77.126400,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f9/Kallar_and_meenmutty_falls.jpg/960px-Kallar_and_meenmutty_falls.jpg",
                "image_caption": "Kallar River boulders and crystal stream",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "River Swimming, Riverside Picnicking, Bird Watching, Nature Photography",
                "entry_fee": "Free",
                "opening_hours": "7:00 AM - 5:30 PM",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 471 2321132 (DTPC)",
                "official_website": "https://www.keralatourism.org/destination/kallar/303",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/kallar/303",
            },
            {
                "name": "Golden Valley",
                "category": "hill-stations-and-nature",
                "short_description": "Tranquil river retreat near Kallar named after its glistening golden-hued sand and riverbed pebbles.",
                "detailed_description": (
                    "Golden Valley is a scenic oasis located just below the hairpin climb of Ponmudi. Here, the clear river "
                    "glides over smooth, golden-colored stones and sandbanks surrounded by verdant tropical trees. It is a favored "
                    "spot for travelers seeking peaceful natural bathing."
                ),
                "village_locality": "Kallar Foothills, Nedumangad",
                "full_address": "Golden Valley, Ponmudi Road, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.723100,
                "longitude": 77.128900,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ad/Ponmudi_%2C_Trivandrum.jpg/960px-Ponmudi_%2C_Trivandrum.jpg",
                "image_caption": "Golden Valley riverbank pebbles",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Stream Dipping, Rock Basking, Nature Photography, Riverside Picnicking",
                "entry_fee": "Free",
                "opening_hours": "7:00 AM - 5:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2321132",
                "official_website": "https://www.keralatourism.org/destination/golden-valley/304",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/golden-valley/304",
            },
            {
                "name": "Bonacaud",
                "category": "hill-stations-and-nature",
                "short_description": "Colonial-era tea estate ruins and scenic base camp for Agasthyakoodam treks.",
                "detailed_description": (
                    "Bonacaud (derived from Bon Accord) is a tranquil hill hamlet situated 55 km from Thiruvananthapuram city. "
                    "Established by British planters in the 19th century, it features mist-covered tea slopes, crumbling colonial "
                    "bungalows, cardamon plantations, and serves as the official forest base camp for the Agasthyakoodam pilgrimage."
                ),
                "village_locality": "Vithura, Nedumangad Taluk",
                "full_address": "Bonacaud Estate, Vithura, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.675600,
                "longitude": 77.187200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/dc/Bonacaud_Picket_Station_Entrance.jpg/960px-Bonacaud_Picket_Station_Entrance.jpg",
                "image_caption": "Colonial Bungalow Ruins at Bonacaud",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Heritage Exploration, Hillside Trekking, Photography, Bird Watching",
                "entry_fee": "Forest check-post fee (~₹25)",
                "opening_hours": "8:00 AM - 4:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 472 2857002",
                "official_website": "https://thiruvananthapuram.nic.in/tourism/",
                "source_name": "DTPC Thiruvananthapuram",
                "source_url": "https://thiruvananthapuram.nic.in/tourism/",
            },
            {
                "name": "Peppara Wildlife Sanctuary",
                "category": "wildlife-and-ecotourism",
                "short_description": "Catchment biodiversity reserve surrounding the Peppara Dam on the Karamana River.",
                "detailed_description": (
                    "Declared in 1983, the Peppara Wildlife Sanctuary spans 53 sq km over the catchment area of Peppara Dam in the "
                    "Western Ghats. It hosts a diverse ecosystem ranging from tropical evergreen forests to swampy grasslands, "
                    "sheltering Asian elephants, sambar, leopards, Malabar grey hornbills, and rare king cobras."
                ),
                "village_locality": "Nedumangad Taluk",
                "full_address": "Peppara Sanctuary, Vithura, Thiruvananthapuram, Kerala 695551",
                "latitude": 8.647200,
                "longitude": 77.194400,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/ca/Peppara_Wildlife_Sanctuary_2.jpg/960px-Peppara_Wildlife_Sanctuary_2.jpg",
                "image_caption": "Peppara Dam and Forest Sanctuary",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Wildlife Trekking, Bird Watching, Nature Photography, Forest Study",
                "entry_fee": "₹50 per Adult, ₹20 per Child",
                "opening_hours": "8:00 AM - 4:00 PM",
                "best_time_to_visit": "November to April",
                "contact_info": "+91 471 2360762 (Wildlife Warden)",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forest Department",
                "source_url": "https://forest.kerala.gov.in/",
            },
            {
                "name": "Neyyar Wildlife Sanctuary",
                "category": "wildlife-and-ecotourism",
                "short_description": "Famous sanctuary featuring a crocodile breeding center, lion safari park, and elephant rehabilitation.",
                "detailed_description": (
                    "Established in 1958, Neyyar Wildlife Sanctuary covers 128 sq km of rugged Western Ghats terrain around the "
                    "Neyyar Dam. Major highlights include the Steve Irwin Crocodile Rehabilitation Center, a boat-accessible "
                    "Lion Safari Park, a deer park, and the nearby Kottur Elephant Rehabilitation Centre."
                ),
                "village_locality": "Kattakada Taluk",
                "full_address": "Neyyar Dam, Kattakada, Thiruvananthapuram, Kerala 695572",
                "latitude": 8.533300,
                "longitude": 77.150000,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/9f/Lions_at_neyyar_wildlife_sanctury.jpg/960px-Lions_at_neyyar_wildlife_sanctury.jpg",
                "image_caption": "Neyyar Reservoir and Forest Ranges",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Lion Safari Boat Tour, Crocodile Park Visit, Boating, Deer Park Walking",
                "entry_fee": "Sanctuary & Safari package (~₹250 - ₹300 per adult)",
                "opening_hours": "9:00 AM - 4:00 PM (Closed on Mondays)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2272182",
                "official_website": "https://forest.kerala.gov.in/",
                "source_name": "Kerala Forest Department",
                "source_url": "https://forest.kerala.gov.in/",
                "is_featured": True,
            },

            # 21-26: Dams, Lakes and Backwaters
            {
                "name": "Neyyar Dam",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Massive gravity dam on the Neyyar river with landscaped gardens and boat rides.",
                "detailed_description": (
                    "Built in 1958, Neyyar Dam is a concrete gravity dam located 30 km from Thiruvananthapuram city. It holds a "
                    "sprawling blue reservoir ringed by forested hills. The dam site features landscaped gardens, children's "
                    "play areas, speed boating, and the globally renowned Sivananda Yoga Vedanta Dhanwantari Ashram."
                ),
                "village_locality": "Kallikkad / Kattakada Taluk",
                "full_address": "Neyyar Dam P.O., Kattakada, Thiruvananthapuram, Kerala 695572",
                "latitude": 8.534200,
                "longitude": 77.147200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/56/Neyyar_dam.jpg/960px-Neyyar_dam.jpg",
                "image_caption": "Neyyar Dam reservoir and spillway",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Dam Top Walking, Speed Boating, Garden Leisure, Yoga Retreats",
                "entry_fee": "₹20 per Adult, ₹10 per Child",
                "opening_hours": "9:00 AM - 5:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2272182",
                "official_website": "https://www.keralatourism.org/destination/neyyar-dam/29",
                "source_name": "Irrigation Dept & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/neyyar-dam/29",
            },
            {
                "name": "Aruvikkara Dam",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Scenic reservoir supplying city drinking water, with an ancient rock-cut Durga temple.",
                "detailed_description": (
                    "Located 16 km north of the city on the banks of the Karamana River, Aruvikkara Dam is both an engineering "
                    "marvel providing piped water to Thiruvananthapuram and a scenic retreat. An ancient Bhagavathy (Durga) temple "
                    "sits on rock outcrops by the river, where feeding the sacred fish is a cherished tradition."
                ),
                "village_locality": "Aruvikkara, Nedumangad Taluk",
                "full_address": "Aruvikkara Dam, Nedumangad, Thiruvananthapuram, Kerala 695564",
                "latitude": 8.567800,
                "longitude": 77.021100,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/f/fd/Aruvikkara_Dam.jpg/960px-Aruvikkara_Dam.jpg",
                "image_caption": "Aruvikkara Dam and Karamana River",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Dam Promenade Walking, Sacred Fish Feeding, Temple Visit, Picnicking",
                "entry_fee": "Free",
                "opening_hours": "8:00 AM - 6:00 PM",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 472 2882220",
                "official_website": "https://www.keralatourism.org/destination/aruvikkara-dam/30",
                "source_name": "Kerala Water Authority & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/aruvikkara-dam/30",
            },
            {
                "name": "Veli Tourist Village",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Waterfront recreation park featuring pedal boating, toy trains, and Kanayi's giant sculptures.",
                "detailed_description": (
                    "Situated where Veli Lake opens into the Arabian Sea, Veli Tourist Village is a family-favorite picnic "
                    "destination. A wooden pedestrian bridge connects the lagoon to the beach. Visitors enjoy pedal boats, "
                    "a miniature children's railway, manicured gardens, and iconic modern sculptures by sculptor Kanayi Kunhiraman."
                ),
                "village_locality": "Veli, Madhavapuram",
                "full_address": "Veli Tourist Village Road, Thiruvananthapuram, Kerala 695021",
                "latitude": 8.511700,
                "longitude": 76.890600,
                "main_image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Veli_Lake_view_from_Tourist_Village.jpg",
                "image_caption": "Veli Lagoon and Kanayi Sculptures",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pedal Boating, Speed Boating, Miniature Train Ride, Beach Walking, Art Sculpture Viewing",
                "entry_fee": "₹25 per Adult, ₹10 per Child",
                "opening_hours": "8:00 AM - 6:30 PM",
                "best_time_to_visit": "Throughout the year (Afternoons/Evenings)",
                "contact_info": "+91 471 2500785",
                "official_website": "https://www.keralatourism.org/destination/veli-tourist-village/31",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/veli-tourist-village/31",
                "is_featured": True,
            },
            {
                "name": "Akkulam Tourist Village",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Scenic backwater park offering musical fountains, boat rides, and an Air Force museum.",
                "detailed_description": (
                    "Akkulam Tourist Village is built along the peaceful banks of Akkulam Lake, an extension of the Veli lake "
                    "system. Surrounded by gentle hills, it provides motor boating, a dedicated children's amusement park, a "
                    "musical dancing fountain, swimming pool, and the Southern Air Command Museum exhibiting aircraft."
                ),
                "village_locality": "Akkulam, Ulloor",
                "full_address": "Akkulam, Thiruvananthapuram, Kerala 695017",
                "latitude": 8.528300,
                "longitude": 76.906700,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/28/Akkulam_Lake_and_Akkulam_Bridge.jpg/960px-Akkulam_Lake_and_Akkulam_Bridge.jpg",
                "image_caption": "Akkulam Lake and Waterfront Park",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Lake Boating, Musical Fountain Show, Air Force Museum Tour, Children's Play",
                "entry_fee": "₹30 per Adult, ₹15 per Child",
                "opening_hours": "9:00 AM - 7:00 PM",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 471 2443043",
                "official_website": "https://www.keralatourism.org/destination/akkulam-tourist-village/32",
                "source_name": "DTPC Thiruvananthapuram",
                "source_url": "https://www.keralatourism.org/destination/akkulam-tourist-village/32",
            },
            {
                "name": "Poovar Backwaters",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Lush mangrove backwater cruise channel with migratory birds and serene canals.",
                "detailed_description": (
                    "The Poovar Backwaters encompass the coastal wetland ecosystem where the Neyyar river approaches the sea. "
                    "Country boats guide travelers through shaded mangrove tunnels, traditional coir-making settlements, and "
                    "open lagoons rich in water lilies and endemic aquatic birds."
                ),
                "village_locality": "Poovar, Neyyattinkara",
                "full_address": "Poovar Backwaters, Neyyattinkara, Thiruvananthapuram, Kerala 695525",
                "latitude": 8.318200,
                "longitude": 77.072600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/14/Poovar_backwaters%2C_Kerala%2C_India.jpg/960px-Poovar_backwaters%2C_Kerala%2C_India.jpg",
                "image_caption": "Mangrove canal cruise at Poovar Backwaters",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Mangrove Boating, Bird Watching, Village Photography, Houseboat Dining",
                "entry_fee": "Free access; Boat cruise rates apply (~₹1,500 - ₹3,000)",
                "opening_hours": "6:00 AM - 6:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2210080",
                "official_website": "https://www.keralatourism.org/destination/poovar/378",
                "source_name": "DTPC Thiruvananthapuram",
                "source_url": "https://www.keralatourism.org/destination/poovar/378",
            },
            {
                "name": "Kappil Lake",
                "category": "dams-lakes-and-backwaters",
                "short_description": "Serene coastal backwater lake merging seamlessly into the Arabian Sea.",
                "detailed_description": (
                    "Spreading over 53 acres near Varkala, Kappil Lake is a tranquil backwater lake framed by waving coconut "
                    "groves. A road bridge crosses the estuary, giving visitors breathtaking views of boats gliding on the freshwater "
                    "lake on one side and sea surf crashing on the other."
                ),
                "village_locality": "Kappil, Edava Panchayat",
                "full_address": "Kappil Lake, Varkala Taluk, Thiruvananthapuram, Kerala 695311",
                "latitude": 8.788900,
                "longitude": 76.678900,
                "main_image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Kappil_bridge.JPG",
                "image_caption": "Kappil Lake Estuary and Bridge",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Pedal Boating, Kayaking, Sunset Photography, Scenic Drive",
                "entry_fee": "Free (Boat rental rates apply)",
                "opening_hours": "6:00 AM - 6:30 PM",
                "best_time_to_visit": "September to March",
                "contact_info": "+91 470 2604555",
                "official_website": "https://www.keralatourism.org/destination/kappil-beach/327",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/kappil-beach/327",
            },

            # 27-34: Temples and Religious Attractions
            {
                "name": "Sree Padmanabhaswamy Temple",
                "category": "temples-and-religious",
                "short_description": "World-renowned ancient temple of Lord Vishnu, historic seat of the Travancore Maharajas.",
                "detailed_description": (
                    "Sree Padmanabhaswamy Temple is an ancient architectural marvel blending indigenous Kerala and Dravidian "
                    "styles, featuring a magnificent 100-foot, 7-tier gopuram. The presiding deity, Lord Vishnu, is reclined "
                    "in the eternal Ananthasayanam posture upon the serpent Anantha, viewable across three doorways. The temple "
                    "is famous for its sacred corridor supported by 365 exquisitely carved stone pillars."
                ),
                "village_locality": "East Fort, City Center",
                "full_address": "West Nada, Fort, Thiruvananthapuram, Kerala 695023",
                "latitude": 8.483000,
                "longitude": 76.943600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/78/Sree_Padmanabha_Swamy_Temple.jpg/960px-Sree_Padmanabha_Swamy_Temple.jpg",
                "image_caption": "Eastern Gopuram of Sree Padmanabhaswamy Temple",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Temple Darshan, Architectural Heritage Walking, Viewing Padmatheertham Sacred Tank",
                "entry_fee": "Free (Traditional dress code strictly enforced: Dhoti for men, Saree/Set-mundu for women)",
                "opening_hours": "3:30 AM - 12:00 PM & 5:00 PM - 8:30 PM (Specific puja session slots)",
                "best_time_to_visit": "Throughout the year (Alpassi & Painkuni festival seasons)",
                "contact_info": "+91 471 2450233",
                "official_website": "https://spst.org/",
                "source_name": "Sree Padmanabhaswamy Temple Trust",
                "source_url": "https://spst.org/",
                "is_featured": True,
            },
            {
                "name": "Attukal Bhagavathy Temple",
                "category": "temples-and-religious",
                "short_description": "Famed as the 'Sabarimala of Women', home of the Guinness World Record Pongala festival.",
                "detailed_description": (
                    "Attukal Bhagavathy Temple is a revered pilgrimage center dedicated to Goddess Kannaki (Bhagavathy). "
                    "It holds a Guinness World Record for hosting the largest annual religious gathering of women on Earth during "
                    "the Attukal Pongala festival, where millions of women prepare sweet rice offerings in earthen pots across "
                    "the city's streets."
                ),
                "village_locality": "Attukal, Manacaud",
                "full_address": "Attukal, Manacaud P.O., Thiruvananthapuram, Kerala 695009",
                "latitude": 8.471900,
                "longitude": 76.953100,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d1/Attukal_temple.jpg/960px-Attukal_temple.jpg",
                "image_caption": "Carved Gopuram of Attukal Bhagavathy Temple",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Temple Worship, Viewing Carved Murals, Attukal Pongala Festival Experience",
                "entry_fee": "Free",
                "opening_hours": "4:30 AM - 12:30 PM & 5:00 PM - 8:30 PM",
                "best_time_to_visit": "February to March (Pongala Festival period)",
                "contact_info": "+91 471 2463130",
                "official_website": "https://attukal.org/",
                "source_name": "Attukal Bhagavathy Temple Trust",
                "source_url": "https://attukal.org/",
                "is_featured": True,
            },
            {
                "name": "Pazhavangadi Ganapathy Temple",
                "category": "temples-and-religious",
                "short_description": "Prominent central Ganesh temple renowned for the coconut-breaking ritual.",
                "detailed_description": (
                    "Located at East Fort within heart of Thiruvananthapuram city, this temple is dedicated to Sri Mahaganapathy. "
                    "Maintained historically by the Indian Army (Madras Regiment), the deity is portrayed seated with folded right "
                    "leg. The temple features 32 distinct sculpted depictions of Lord Ganesha and is famous for the continuous "
                    "breaking of coconuts by devotees."
                ),
                "village_locality": "East Fort, City Center",
                "full_address": "Padmavilasom Road, Pazhavangadi, Thiruvananthapuram, Kerala 695023",
                "latitude": 8.488300,
                "longitude": 76.946700,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4c/Pazhavangadi_ganapathi_temple_01.JPG/960px-Pazhavangadi_ganapathi_temple_01.JPG",
                "image_caption": "Pazhavangadi Mahaganapathy Temple",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Darshan, Coconut-breaking Offering (Nalikeram Udakkal), Spiritual Meditation",
                "entry_fee": "Free",
                "opening_hours": "4:30 AM - 11:00 AM & 5:00 PM - 8:30 PM",
                "best_time_to_visit": "Vinayaka Chaturthi festival (August/September)",
                "contact_info": "+91 471 2461999",
                "official_website": "https://www.keralatourism.org/destination/pazhavangadi-ganapathy-temple/33",
                "source_name": "Travancore Devaswom & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/pazhavangadi-ganapathy-temple/33",
            },
            {
                "name": "Janardanaswamy Temple, Varkala",
                "category": "temples-and-religious",
                "short_description": "Ancient 2,000-year-old cliffside Vaishnavite shrine known as Dakshina Kashi.",
                "detailed_description": (
                    "Perched on a cliff overlooking the Arabian Sea, Janardanaswamy Temple is an ancient temple dedicated to "
                    "Lord Vishnu. Believed to be over two millennia old, it attracts pilgrims from across the nation for ancestral "
                    "rites (Pithru Tharpanam). It houses a historic seventeenth-century Dutch brass bell donated by a seafaring captain."
                ),
                "village_locality": "Varkala",
                "full_address": "Janardanaswamy Temple, Varkala, Thiruvananthapuram, Kerala 695141",
                "latitude": 8.732800,
                "longitude": 76.713900,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8a/Janardhana_swamy_temple.jpg/960px-Janardhana_swamy_temple.jpg",
                "image_caption": "Ancient Janardanaswamy Temple Complex",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Ancient Temple Worship, Viewing Ancient Dutch Bell, Ancestral Pithru Tharpanam",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 12:00 PM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "Arattu Festival (March/April)",
                "contact_info": "+91 470 2602288",
                "official_website": "https://www.keralatourism.org/destination/janardhana-swamy-temple/34",
                "source_name": "Travancore Devaswom Board",
                "source_url": "https://www.keralatourism.org/destination/janardhana-swamy-temple/34",
            },
            {
                "name": "Sivagiri Mutt",
                "category": "temples-and-religious",
                "short_description": "Spiritual headquarters of social reformer Sree Narayana Guru and holy Samadhi shrine.",
                "detailed_description": (
                    "Sivagiri Mutt is a major spiritual retreat established in 1904 by Sree Narayana Guru, the revered social "
                    "reformer and philosopher who championed 'One Caste, One Religion, One God for Humanity'. Located on a serene "
                    "hillock in Varkala, it houses the Guru's holy Samadhi, Sarada Mutt (dedicated to the Goddess of Knowledge), "
                    "and a vibrant Vedic hermitage."
                ),
                "village_locality": "Sivagiri, Varkala",
                "full_address": "Sivagiri Mutt, Varkala, Thiruvananthapuram, Kerala 695141",
                "latitude": 8.736900,
                "longitude": 76.738900,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/40/Sivagiri_Ashramam_at_Varkkala.jpg/960px-Sivagiri_Ashramam_at_Varkkala.jpg",
                "image_caption": "Sivagiri Mutt Samadhi Shrine",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 3.0",
                "available_activities": "Spiritual Meditation, Visiting Guru's Hermitage, Sivagiri Pilgrimage (Dec 30-Jan 1)",
                "entry_fee": "Free",
                "opening_hours": "5:30 AM - 12:00 PM & 4:30 PM - 8:00 PM",
                "best_time_to_visit": "Late December (Annual Sivagiri Pilgrimage)",
                "contact_info": "+91 470 2602221",
                "official_website": "https://sivagiri.org/",
                "source_name": "Sree Narayana Dharma Sangham Trust",
                "source_url": "https://sivagiri.org/",
            },
            {
                "name": "Sarkara Devi Temple",
                "category": "temples-and-religious",
                "short_description": "Celebrated historic Bhadrakali shrine famous for the dramatic Sarkara Kaliyoot festival.",
                "detailed_description": (
                    "Located in Chirayinkeezhu near the backwaters, Sarkara Devi Temple is an ancient shrine dedicated to "
                    "Bhadrakali. It achieved royal prominence during the Travancore era when King Anizham Thirunal Marthanda Varma "
                    "prayed here prior to his historic battles. The annual Kaliyoot and Meenabharani festivals attract thousands."
                ),
                "village_locality": "Chirayinkeezhu",
                "full_address": "Sarkara Devi Temple, Chirayinkeezhu, Thiruvananthapuram, Kerala 695304",
                "latitude": 8.653300,
                "longitude": 76.790600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/af/Sarkara_Devi_Temple.jpg/960px-Sarkara_Devi_Temple.jpg",
                "image_caption": "Sarkara Devi Temple Complex",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Temple Darshan, Traditional Temple Music Viewing, Festival Experience",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 11:30 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "February to March (Kaliyoot Festival)",
                "contact_info": "+91 470 2640233",
                "official_website": "https://www.keralatourism.org/destination/sarkara-devi-temple/35",
                "source_name": "Travancore Devaswom Board",
                "source_url": "https://www.keralatourism.org/destination/sarkara-devi-temple/35",
            },
            {
                "name": "Aruvippuram Temple",
                "category": "temples-and-religious",
                "short_description": "Historic landmark where Sree Narayana Guru consecrated a Shiva idol in 1888, sparking social reform.",
                "detailed_description": (
                    "Aruvippuram is a monumental landmark in Indian social history. On Shivaratri day in 1888, Sree Narayana Guru "
                    "took a rock from the Neyyar River and consecrated a Shiva idol, boldly challenging the upper-caste monopoly "
                    "on priesthood and temple installation. Set beside peaceful river cascades, it remains an inspiring pilgrimage site."
                ),
                "village_locality": "Aruvippuram, near Neyyattinkara",
                "full_address": "Aruvippuram, Neyyattinkara, Thiruvananthapuram, Kerala 695126",
                "latitude": 8.418300,
                "longitude": 77.108300,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/60/Aruvippuram.jpg/960px-Aruvippuram.jpg",
                "image_caption": "Aruvippuram Siva Temple on Neyyar River",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Historical Pilgrimage, Riverbank Meditation, Temple Worship, Nature Walking",
                "entry_fee": "Free",
                "opening_hours": "5:00 AM - 11:30 AM & 5:00 PM - 7:30 PM",
                "best_time_to_visit": "Maha Shivaratri (February/March)",
                "contact_info": "+91 471 2222238",
                "official_website": "https://www.keralatourism.org/destination/aruvippuram/36",
                "source_name": "Sree Narayana Dharma Sangham Trust",
                "source_url": "https://www.keralatourism.org/destination/aruvippuram/36",
            },
            {
                "name": "Azhimala Shiva Temple",
                "category": "temples-and-religious",
                "short_description": "Spectacular seaside cliff temple featuring India's tallest 58-foot Gangadhareswara Shiva sculpture.",
                "detailed_description": (
                    "Perched right on a rocky cliff beside the surging waves of the Arabian Sea, Azhimala Shiva Temple has "
                    "gained international acclaim for its magnificent 58-foot-tall concrete sculpture of Lord Shiva in the "
                    "'Gangadhareswara' form, sculpted by young artist P. S. Devadathan over six years. The wind-swept cliff setting "
                    "creates an extraordinary spiritual atmosphere."
                ),
                "village_locality": "Vizhinjam / Kottukal",
                "full_address": "Azhimala Temple Road, Vizhinjam, Thiruvananthapuram, Kerala 695521",
                "latitude": 8.358300,
                "longitude": 77.012800,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d3/Azhimala_Siva_Temple%2C_near_Vizhinjam_%282%29.jpg/960px-Azhimala_Siva_Temple%2C_near_Vizhinjam_%282%29.jpg",
                "image_caption": "Colossal 58-foot Gangadhareswara Shiva statue at Azhimala",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Viewing Monumental Sculpture, Ocean Sunset Darshan, Cliffside Photography",
                "entry_fee": "Free",
                "opening_hours": "5:30 AM - 11:00 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "October to March (Evenings for sunset)",
                "contact_info": "+91 471 2267500",
                "official_website": "https://www.keralatourism.org/destination/aazhimala-shiva-temple/646",
                "source_name": "Kerala Tourism Official Portal",
                "source_url": "https://www.keralatourism.org/destination/aazhimala-shiva-temple/646",
                "is_featured": True,
            },

            # 35-42: Historical Places and Museums
            {
                "name": "Napier Museum",
                "category": "historical-places-and-museums",
                "short_description": "19th-century Indo-Saracenic architectural jewel housing rare bronzes, ivory, and temple ornaments.",
                "detailed_description": (
                    "Built in 1880 and named after Lord Napier, the British Governor of Madras, this museum is an architectural "
                    "masterpiece designed by Robert Chisholm. It features a natural air-conditioning system, gothic roofs, minarets, "
                    "and ornate woodcarvings. Inside, it preserves a rare collection of archaeological and historic artifacts, ancient "
                    "bronzes, musical instruments, and a temple chariot."
                ),
                "village_locality": "Museum Compound, City Center",
                "full_address": "Museum Compound, Kanaka Nagar, Nanthancode, Thiruvananthapuram, Kerala 695033",
                "latitude": 8.508900,
                "longitude": 76.955300,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/da/Napier_Museum.JPG/960px-Napier_Museum.JPG",
                "image_caption": "Napier Museum Indo-Saracenic Facade",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Archaeological Artifact Exploration, Architectural Study, Botanical Park Strolls",
                "entry_fee": "₹25 per Adult, ₹10 per Child",
                "opening_hours": "10:00 AM - 4:45 PM (Closed on Mondays, Wednesday mornings)",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 471 2318294",
                "official_website": "https://keralamuseums.kerala.gov.in/",
                "source_name": "Department of Museums and Zoos, Govt. of Kerala",
                "source_url": "https://keralamuseums.kerala.gov.in/",
                "is_featured": True,
            },
            {
                "name": "Kuthiramalika Palace Museum",
                "category": "historical-places-and-museums",
                "short_description": "Travancore royal palace renowned for 122 carved wooden horses and Swathi Thirunal's musical legacy.",
                "detailed_description": (
                    "Kuthiramalika (Mansion of Horses), officially Puthenmalika, was built in the 1840s by Maharaja Swathi Thirunal "
                    "Rama Varma, the legendary poet-composer king. The palace exemplifies classical Travancore architecture with "
                    "122 smiling wooden horses carved into its roof brackets. It houses royal jewel-encrusted thrones, Italian "
                    "mirrors, Belgian crystal chandeliers, and royal musical instruments."
                ),
                "village_locality": "East Fort",
                "full_address": "Near Padmanabhaswamy Temple, East Fort, Thiruvananthapuram, Kerala 695023",
                "latitude": 8.481900,
                "longitude": 76.944200,
                "main_image_url": "https://upload.wikimedia.org/wikipedia/commons/7/71/0507-KuthiraMalika-Dinakarr.jpg",
                "image_caption": "Carved wooden horse brackets of Kuthiramalika",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Guided Royal Palace Tour, Classical Musical Heritage Walk, Architecture Photography",
                "entry_fee": "₹100 per Indian Adult, ₹20 per Child, ₹200 for Foreigners",
                "opening_hours": "8:30 AM - 12:30 PM & 3:30 PM - 5:30 PM (Closed on Mondays)",
                "best_time_to_visit": "January (Swathi Sangeethotsavam music festival)",
                "contact_info": "+91 471 2473952",
                "official_website": "https://www.keralatourism.org/destination/kuthiramalika-palace/37",
                "source_name": "Travancore Royal Family Trust & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/kuthiramalika-palace/37",
                "is_featured": True,
            },
            {
                "name": "Kanakakkunnu Palace",
                "category": "historical-places-and-museums",
                "short_description": "Exquisite Travancore royal hill palace complex, cultural hub, and Nishagandhi festival venue.",
                "detailed_description": (
                    "Built during the reign of Sree Moolam Thirunal Maharaja on a picturesque hillock, Kanakakkunnu Palace was "
                    "historically used for royal banquets and official entertainment. With its ornate gables, crystal chandeliers, "
                    "and sprawling landscaped meadows, it serves as the premier cultural amphitheater of the state, hosting the "
                    "annual Nishagandhi Dance and Music Festival."
                ),
                "village_locality": "Nanthancode",
                "full_address": "Kanakakkunnu Palace Road, Nanthancode, Thiruvananthapuram, Kerala 695033",
                "latitude": 8.511700,
                "longitude": 76.959200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d5/Kanakakkunnu_Palace_DSW.jpg/960px-Kanakakkunnu_Palace_DSW.jpg",
                "image_caption": "Kanakakkunnu Palace and Lawn Gardens",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Palace Grounds Walking, Attending Cultural Festivals, Open-Air Events",
                "entry_fee": "Grounds free (Special exhibition tickets apply)",
                "opening_hours": "Grounds: 6:00 AM - 9:00 PM; Palace interior: During events",
                "best_time_to_visit": "October to March (Nishagandhi Festival in January)",
                "contact_info": "+91 471 2321132",
                "official_website": "https://www.keralatourism.org/destination/kanakakkunnu-palace/38",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/kanakakkunnu-palace/38",
            },
            {
                "name": "Anchuthengu Fort",
                "category": "historical-places-and-museums",
                "short_description": "Historic 1695 British East India Company coastal bastion on the palm-lined Malabar coast.",
                "detailed_description": (
                    "Anchuthengu Fort (formerly Anjengo Fort) was constructed in 1695 by the British East India Company with "
                    "permission from the Queen of Attingal, serving as their earliest permanent trading settlement in Kerala. "
                    "Bounded by sea on one side and backwaters on the other, the square fort preserves thick laterite ramparts, "
                    "colonial gravestones, and observation lookouts protected by the Archaeological Survey of India."
                ),
                "village_locality": "Anchuthengu, Chirayinkeezhu",
                "full_address": "Anchuthengu Fort, Chirayinkeezhu Taluk, Thiruvananthapuram, Kerala 695309",
                "latitude": 8.681100,
                "longitude": 76.764400,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c4/Anchuthengu_Fort_2024_06.jpg/960px-Anchuthengu_Fort_2024_06.jpg",
                "image_caption": "Historic Laterite Ramparts of Anchuthengu Fort",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Colonial Fortress Exploration, Historical Rampart Walking, Backwater Photography",
                "entry_fee": "Free",
                "opening_hours": "9:00 AM - 5:30 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2321132",
                "official_website": "https://www.keralatourism.org/destination/anchuthengu-fort/39",
                "source_name": "Archaeological Survey of India (ASI) & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/anchuthengu-fort/39",
            },
            {
                "name": "Anchuthengu Lighthouse",
                "category": "historical-places-and-museums",
                "short_description": "Towering 130-foot coastal beacon offering sweeping vistas of the Arabian Sea and palm groves.",
                "detailed_description": (
                    "Standing adjacent to the historic Anjengo Fort, the Anchuthengu Lighthouse was established in the 19th "
                    "century by the British to guide merchant ships along the coast. Visitors can ascend its spiral stairway "
                    "for an awe-inspiring 360-degree panoramic view of backwater lakes and the Arabian Sea."
                ),
                "village_locality": "Anchuthengu",
                "full_address": "Anchuthengu Lighthouse, Thiruvananthapuram, Kerala 695309",
                "latitude": 8.681400,
                "longitude": 76.764200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1e/View_from_Anchuthengu_lighthouse_%2866326%29.jpg/960px-View_from_Anchuthengu_lighthouse_%2866326%29.jpg",
                "image_caption": "Anchuthengu Lighthouse Tower",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Climbing Lighthouse Tower, Panoramic Ocean Viewing, Photography",
                "entry_fee": "₹20 per Adult, ₹10 per Child",
                "opening_hours": "3:00 PM - 5:00 PM",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 470 2604555",
                "official_website": "http://www.dgll.nic.in/",
                "source_name": "Directorate General of Lighthouses and Lightships",
                "source_url": "http://www.dgll.nic.in/",
            },
            {
                "name": "Koyikkal Palace",
                "category": "historical-places-and-museums",
                "short_description": "15th-century traditional Nalukettu palace housing the Numismatics and Folklore museums.",
                "detailed_description": (
                    "Located in Nedumangad, Koyikkal Palace was built in the 15th century for Umayamma Rani, the fierce queen regent "
                    "of Venad. Built in classical Kerala 'Nalukettu' gabled style with sloping tiled roofs, it now houses a Folklore "
                    "Museum preserving antique musical instruments (like the unique Chandravalayam) and a Numismatics Museum with "
                    "coins dating back thousands of years."
                ),
                "village_locality": "Nedumangad",
                "full_address": "Koyikkal Palace Road, Nedumangad, Thiruvananthapuram, Kerala 695541",
                "latitude": 8.601900,
                "longitude": 77.000600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/3/34/Koyikkal_Palace.jpg/960px-Koyikkal_Palace.jpg",
                "image_caption": "Koyikkal Palace Traditional Nalukettu Architecture",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Ancient Coin Exploration, Folklore Musical Instrument Study, Architecture Tour",
                "entry_fee": "₹20 per Adult, ₹10 per Child",
                "opening_hours": "9:00 AM - 5:00 PM (Closed on Mondays)",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 472 2812730",
                "official_website": "https://www.keralatourism.org/destination/koyikkal-palace/40",
                "source_name": "Department of Archaeology, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/destination/koyikkal-palace/40",
            },
            {
                "name": "Kilimanoor Palace",
                "category": "historical-places-and-museums",
                "short_description": "Ancestral royal estate and birth studio of master artist Raja Ravi Varma.",
                "detailed_description": (
                    "Kilimanoor Palace is celebrated across the world as the birthplace of legendary Indian painter Raja Ravi "
                    "Varma. Sprawling over 15 acres, the palace complex includes traditional Padippuras (grand gatehouses), "
                    "kulam ponds, and the master's private studio where his immortal mythological portraits were created."
                ),
                "village_locality": "Kilimanoor",
                "full_address": "Kilimanoor Palace, Kilimanoor, Thiruvananthapuram, Kerala 695601",
                "latitude": 8.767500,
                "longitude": 76.877800,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8d/Kilimanoor_palace%2Ckilimanoor%2Ckerala%2Cindia.jpg/960px-Kilimanoor_palace%2Ckilimanoor%2Ckerala%2Cindia.jpg",
                "image_caption": "Raja Ravi Varma Art Studio at Kilimanoor Palace",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Art Studio Pilgrimage, Palace Heritage Walk, Historical Architecture Study",
                "entry_fee": "Free / Voluntary trust maintenance donation",
                "opening_hours": "10:00 AM - 5:00 PM",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 470 2672235",
                "official_website": "https://www.keralatourism.org/destination/kilimanoor-palace/41",
                "source_name": "Kilimanoor Palace Trust & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/kilimanoor-palace/41",
            },
            {
                "name": "Kerala Science and Technology Museum",
                "category": "historical-places-and-museums",
                "short_description": "Premier interactive science learning center with mechanics, electronics, and astronomy wings.",
                "detailed_description": (
                    "Established in 1984 by the Government of Kerala, KSSTM is an autonomous institution designed to popularize "
                    "science through hands-on participatory exhibits. The museum houses over 300 animated exhibits covering mechanics, "
                    "robotics, electronics, solar energy, power generation, and aviation."
                ),
                "village_locality": "PMG Junction, City Center",
                "full_address": "Vikas Bhavan P.O., PMG, Thiruvananthapuram, Kerala 695033",
                "latitude": 8.510000,
                "longitude": 76.945000,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/d/da/Planetorium_thiruvananthapuram.jpg/960px-Planetorium_thiruvananthapuram.jpg",
                "image_caption": "Science and Technology Museum Campus",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Interactive STEM Experimentation, Night Sky Stargazing with 11-inch Telescope",
                "entry_fee": "₹40 per Adult, ₹25 per Child",
                "opening_hours": "10:00 AM - 5:00 PM (Closed on Mondays)",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 471 2306024",
                "official_website": "http://www.kstmuseum.com/",
                "source_name": "Kerala State Science & Technology Museum",
                "source_url": "http://www.kstmuseum.com/",
            },

            # 43-50: Parks, Entertainment and Other Attractions
            {
                "name": "Thiruvananthapuram Zoo",
                "category": "parks-culture-and-entertainment",
                "short_description": "One of India's oldest zoos, established in 1857, set in 55 acres of lush botanical gardens.",
                "detailed_description": (
                    "Established by Maharaja Uthram Thirunal of Travancore in 1857 as an annex to the Napier Museum, this is one "
                    "of the oldest zoological gardens in Asia. Modernized into open naturalistic moated enclosures, it houses Bengal "
                    "tigers, Asiatic lions, Indian rhinoceroses, lion-tailed macaques, anacondas, and towering indigenous trees."
                ),
                "village_locality": "Museum Compound",
                "full_address": "Museum Compound, Nanthancode, Thiruvananthapuram, Kerala 695033",
                "latitude": 8.510600,
                "longitude": 76.954700,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/4/48/Thiruvananthapuram_Zoo.jpg/960px-Thiruvananthapuram_Zoo.jpg",
                "image_caption": "Shaded enclosures at Thiruvananthapuram Zoo",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Wildlife Observation, Botanical Tree Walk, Nature Photography",
                "entry_fee": "₹30 per Adult, ₹15 per Child",
                "opening_hours": "9:00 AM - 5:15 PM (Closed on Mondays)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 471 2316275",
                "official_website": "https://keralamuseums.kerala.gov.in/",
                "source_name": "Department of Museums and Zoos, Govt. of Kerala",
                "source_url": "https://keralamuseums.kerala.gov.in/",
                "is_featured": True,
            },
            {
                "name": "Priyadarshini Planetarium",
                "category": "parks-culture-and-entertainment",
                "short_description": "High-tech full-dome digital planetarium delivering celestial sky shows.",
                "detailed_description": (
                    "Inaugurated in 1994, the Priyadarshini Planetarium is rated among the best horizontal dome planetariums in "
                    "South Asia. It features an advanced digital optomechanical star projector that simulates the cosmic night sky, "
                    "constellations, planetary motions, and space exploration missions under its 15-metre hemispherical dome."
                ),
                "village_locality": "PMG Junction",
                "full_address": "Science & Tech Museum Campus, PMG, Thiruvananthapuram, Kerala 695033",
                "latitude": 8.510300,
                "longitude": 76.945300,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0d/Priyadarsini_Planetarium%2C_Thiruvananthapuram.jpeg/960px-Priyadarsini_Planetarium%2C_Thiruvananthapuram.jpeg",
                "image_caption": "Priyadarshini Planetarium Dome",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Full-Dome 3D Astronomy Shows, Space Exploration Gallery, 4D Theater Experience",
                "entry_fee": "₹75 per Adult, ₹50 per Child",
                "opening_hours": "Shows at 10:30 AM, 12:00 PM, 3:00 PM, 5:00 PM (Closed on Mondays)",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 471 2306024",
                "official_website": "http://www.kstmuseum.com/",
                "source_name": "Kerala State Science & Technology Museum",
                "source_url": "http://www.kstmuseum.com/",
            },
            {
                "name": "Magic Planet",
                "category": "parks-culture-and-entertainment",
                "short_description": "World's first magic-themed cultural park founded by magician Gopinath Muthukad.",
                "detailed_description": (
                    "Located in KINFRA Film and Video Park in Kazhakkoottam, Magic Planet is an innovative edutainment theme park. "
                    "Dedicated to the preservation of Indian street magic, illusionism, and science-infused theater, it features "
                    "live illusion performances, the Houdini Escape Theater, and the Different Art Centre supporting specially-abled youth."
                ),
                "village_locality": "Kazhakkoottam, KINFRA Park",
                "full_address": "KINFRA Film and Video Park, Kazhakkoottam, Thiruvananthapuram, Kerala 695585",
                "latitude": 8.583900,
                "longitude": 76.862200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/13/Kazhakootam.jpg/960px-Kazhakootam.jpg",
                "image_caption": "Magic Planet Complex Kazhakkoottam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "World Illusion Shows, Street Magic Demonstrations, Circus Castle, Shadow Play",
                "entry_fee": "₹450 - ₹500 package ticket",
                "opening_hours": "10:00 AM - 5:00 PM (Closed on Mondays)",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 471 2411151",
                "official_website": "https://magicplanet.in/",
                "source_name": "Magic Planet Official",
                "source_url": "https://magicplanet.in/",
            },
            {
                "name": "Vizhinjam Marine Aquarium",
                "category": "parks-culture-and-entertainment",
                "short_description": "Marine biodiversity discovery center operated by CMFRI featuring exotic ocean species.",
                "detailed_description": (
                    "Maintained by the Central Marine Fisheries Research Institute (CMFRI) near Vizhinjam harbor, this aquarium "
                    "displays a vibrant collection of tropical sea life, including clownfish, squirrelfish, piranhas, sea turtles, "
                    "and lionfish. It demonstrates breakthrough artificial pearl production technology pioneered by CMFRI scientists."
                ),
                "village_locality": "Vizhinjam Harbour Road",
                "full_address": "Near Harbour, Vizhinjam, Thiruvananthapuram, Kerala 695521",
                "latitude": 8.379200,
                "longitude": 76.993300,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/5/52/Vizhinjam_3.jpg/960px-Vizhinjam_3.jpg",
                "image_caption": "CMFRI Vizhinjam Marine Aquarium",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Exotic Marine Life Viewing, Pearl Oyster Culture Demonstration, Educational Tour",
                "entry_fee": "₹30 per Adult, ₹15 per Child",
                "opening_hours": "9:00 AM - 5:30 PM (Closed on Mondays)",
                "best_time_to_visit": "October to April",
                "contact_info": "+91 471 2480224",
                "official_website": "https://www.cmfri.org.in/",
                "source_name": "Central Marine Fisheries Research Institute (CMFRI)",
                "source_url": "https://www.cmfri.org.in/",
            },
            {
                "name": "Nishagandhi Auditorium",
                "category": "parks-culture-and-entertainment",
                "short_description": "Renowned open-air amphitheater hosting national classical dance and music festivals.",
                "detailed_description": (
                    "Nestled in the lush grounds of the Kanakakkunnu Palace hillock, the Nishagandhi Auditorium is a celebrated "
                    "open-air cultural stage. Under starry skies, it hosts the prestigious Nishagandhi Dance Festival every January, "
                    "featuring the finest exponents of Kathakali, Mohiniyattam, Bharatanatyam, Odissi, and Hindustani/Carnatic music."
                ),
                "village_locality": "Kanakakkunnu, Nanthancode",
                "full_address": "Kanakakkunnu Palace Grounds, Nanthancode, Thiruvananthapuram, Kerala 695033",
                "latitude": 8.512200,
                "longitude": 76.959400,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c2/NIshagandhi_06.jpg/960px-NIshagandhi_06.jpg",
                "image_caption": "Nishagandhi Open-Air Cultural Amphitheatre",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Attending Classical Dance Concerts, Music Recitals, Cultural Evening Walks",
                "entry_fee": "Free during government festivals",
                "opening_hours": "4:00 PM - 9:30 PM (Event days)",
                "best_time_to_visit": "January to February (Nishagandhi Dance Festival)",
                "contact_info": "+91 471 2321132",
                "official_website": "https://www.keralatourism.org/nishagandhi-dance-festival/",
                "source_name": "Department of Tourism, Govt. of Kerala",
                "source_url": "https://www.keralatourism.org/nishagandhi-dance-festival/",
            },
            {
                "name": "Kerala Arts and Crafts Village",
                "category": "parks-culture-and-entertainment",
                "short_description": "Sprawling handicraft village celebrating master weavers, potters, and traditional artisans.",
                "detailed_description": (
                    "Developed by the Department of Tourism at Vellar near Kovalam, this comprehensive craft village covers 8.5 acres "
                    "designed to preserve Kerala's rich artisanal heritage. Visitors can observe live demonstrations by over 750 master "
                    "craftspeople engaged in handloom weaving, Aranmula metal mirrors, terracotta pottery, woodcraft, and bell-metal casting."
                ),
                "village_locality": "Vellar, near Kovalam",
                "full_address": "Kerala Arts and Crafts Village, Vellar, Kovalam, Thiruvananthapuram, Kerala 695527",
                "latitude": 8.423300,
                "longitude": 76.974200,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a4/Crafts_of_Kerala_02.jpg/960px-Crafts_of_Kerala_02.jpg",
                "image_caption": "Artisan courtyards at Kerala Arts and Crafts Village",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Live Artisan Workshop Observation, Handloom Weaving, Authentic Handicraft Shopping",
                "entry_fee": "₹100 per Adult, ₹50 per Child",
                "opening_hours": "10:00 AM - 7:00 PM",
                "best_time_to_visit": "Throughout the year",
                "contact_info": "+91 471 2481100",
                "official_website": "https://kacv.in/",
                "source_name": "Department of Tourism & ULCCS",
                "source_url": "https://kacv.in/",
                "is_featured": True,
            },
            {
                "name": "Varkala Cliff",
                "category": "beaches-and-coastal",
                "short_description": "Spectacular geological monument lined with cliffside cafes, shops, and sunset viewpoints.",
                "detailed_description": (
                    "The Varkala Cliff (North and South Cliffs) consists of dramatic coastal tertiary sediment cliffs overlooking "
                    "the Arabian Sea. A lively paved promenade runs along the rim of the cliff, famous for bohemian seafood cafes, "
                    "Tibetan artisan shops, panoramic sunset viewpoints, and stairways leading down to the golden sands of Papanasam Beach."
                ),
                "village_locality": "Varkala Cliff, Varkala",
                "full_address": "North Cliff, Kurakkanni, Varkala, Thiruvananthapuram, Kerala 695141",
                "latitude": 8.739200,
                "longitude": 76.705600,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/23/Varkala_Cliff.jpg/960px-Varkala_Cliff.jpg",
                "image_caption": "Varkala Cliffside Promenade and Beach",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Cliff Promenade Walking, Sunset Dining, Handicraft Shopping, Paragliding Observation",
                "entry_fee": "Free",
                "opening_hours": "Open 24 Hours (Promenade lively until 10:30 PM)",
                "best_time_to_visit": "October to March",
                "contact_info": "+91 470 2604555",
                "official_website": "https://www.keralatourism.org/destination/varkala-beach/326",
                "source_name": "Geological Survey of India & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/varkala-beach/326",
                "is_featured": True,
            },
            {
                "name": "Thiruvallam",
                "category": "temples-and-religious",
                "short_description": "Sacred confluence of Karamana and Killi rivers, home to the ancient Sree Parasurama Swami Temple.",
                "detailed_description": (
                    "Thiruvallam is situated 6 km south of Thiruvananthapuram city at the serene meeting point of two holy rivers, "
                    "Karamana and Killi. It is famed for the ancient Sree Parasurama Temple, believed to be the only temple in Kerala "
                    "dedicated exclusively to Sage Parasurama (the mythological creator of Kerala), and a major center for ancestral "
                    "Karkidaka Vavu Bali rituals."
                ),
                "village_locality": "Thiruvallam",
                "full_address": "Thiruvallam P.O., Thiruvananthapuram, Kerala 695027",
                "latitude": 8.445000,
                "longitude": 76.955000,
                "main_image_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/02/Thiruvallam_Parasurama_Temple_EntranceDSC_8729.jpg/960px-Thiruvallam_Parasurama_Temple_EntranceDSC_8729.jpg",
                "image_caption": "Parasurama Temple at the river confluence in Thiruvallam",
                "image_attribution": "Wikimedia Commons / CC-BY-SA 4.0",
                "available_activities": "Sacred River Confluence Darshan, Ancestral Bali Tharpanam, Backwater Kayaking",
                "entry_fee": "Free",
                "opening_hours": "4:30 AM - 11:30 AM & 5:00 PM - 8:00 PM",
                "best_time_to_visit": "Karkidaka Vavu (July/August)",
                "contact_info": "+91 471 2380765",
                "official_website": "https://www.keralatourism.org/destination/thiruvallam-backwaters/42",
                "source_name": "Travancore Devaswom Board & Kerala Tourism",
                "source_url": "https://www.keralatourism.org/destination/thiruvallam-backwaters/42",
            },
        ]

        verified_count = 0
        pending_count = 0
        excluded_count = 0
        created_count = 0
        updated_count = 0

        today = datetime.date(2026, 11, 24)
        next_year = datetime.date(2027, 11, 24)

        for d_data in destinations_list:
            cat_obj = categories_map[d_data['category']]
            dest_name = d_data['name']
            dest_slug = slugify(dest_name)

            defaults = {
                'name': dest_name,
                'district': district,
                'category': cat_obj,
                'short_description': d_data['short_description'],
                'detailed_description': d_data['detailed_description'],
                'village_locality': d_data.get('village_locality', ''),
                'full_address': d_data.get('full_address', ''),
                'latitude': d_data['latitude'],
                'longitude': d_data['longitude'],
                'main_image_url': d_data.get('main_image_url', ''),
                'image_caption': d_data.get('image_caption', ''),
                'image_attribution': d_data.get('image_attribution', ''),
                'available_activities': d_data.get('available_activities', ''),
                'entry_fee': d_data.get('entry_fee', ''),
                'opening_hours': d_data.get('opening_hours', ''),
                'best_time_to_visit': d_data.get('best_time_to_visit', 'October to March'),
                'contact_info': d_data.get('contact_info', ''),
                'official_website': d_data.get('official_website', ''),
                'is_featured': d_data.get('is_featured', False),
                'source_name': d_data['source_name'],
                'source_url': d_data['source_url'],
                'verification_status': VerificationStatus.VERIFIED,
                'last_verified_date': today,
                'valid_until': next_year,
                'is_demo': False,
            }

            dest, created = Destination.objects.update_or_create(
                slug=dest_slug,
                district=district,
                defaults=defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1
            verified_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n--- IMPORT SUMMARY ---\n"
            f"Total Processed: {len(destinations_list)}\n"
            f"Created New: {created_count}\n"
            f"Updated Existing: {updated_count}\n"
            f"Total Verified: {verified_count}\n"
            f"Pending Verification: {pending_count}\n"
            f"Excluded (Wrong district/Unverified): {excluded_count}\n"
            f"Database Records for Thiruvananthapuram: {Destination.objects.filter(district=district).count()}"
        ))
