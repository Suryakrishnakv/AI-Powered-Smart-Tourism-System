from django.shortcuts import render
from django.db.models import Count
from destinations.models import District


def home(request):
    """Landing homepage for Kerala Smart Tourism System."""
    district_names = [
        "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
        "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
        "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
    ]
    active_districts = {
        d.name: {"slug": d.slug, "count": d.dest_count}
        for d in District.objects.annotate(dest_count=Count("destinations"))
        if d.dest_count > 0
    }
    districts = [
        {
            "name": name,
            "slug": active_districts[name]["slug"] if name in active_districts else None,
            "count": active_districts[name]["count"] if name in active_districts else 0,
        }
        for name in district_names
    ]
    categories = [
        {"name": "Hill Stations", "icon": "bi-triangle", "desc": "Misty peaks & tea gardens of Munnar & Wayanad"},
        {"name": "Beaches", "icon": "bi-water", "desc": "Golden shores of Kovalam, Varkala & Kollam"},
        {"name": "Backwaters", "icon": "bi-tsunami", "desc": "Serene houseboat trails in Ashtamudi & Alappuzha"},
        {"name": "Waterfalls", "icon": "bi-moisture", "desc": "Cascades of Athirappilly, Meenmutty & Palaruvi"},
        {"name": "Wildlife Sanctuaries", "icon": "bi-shield-check", "desc": "Periyar, Shendurney & Wayanad reserves"},
        {"name": "Heritage & Culture", "icon": "bi-bank", "desc": "Fort Kochi, Punalur Bridge & royal palaces"}
    ]
    return render(request, 'home.html', {
        'districts': districts,
        'categories': categories,
    })


def about(request):
    """About Kerala Smart Tourism."""
    return render(request, 'about.html')
