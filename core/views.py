from django.shortcuts import render

def home(request):
    """Landing homepage for Kerala Smart Tourism System."""
    districts = [
        "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
        "Kottayam", "Idukki", "Ernakulam", "Thrissur", "Palakkad",
        "Malappuram", "Kozhikode", "Wayanad", "Kannur", "Kasaragod"
    ]
    categories = [
        {"name": "Hill Stations", "icon": "bi-triangle", "desc": "Misty peaks & tea gardens of Munnar & Wayanad"},
        {"name": "Beaches", "icon": "bi-water", "desc": "Golden shores of Kovalam, Varkala & Marari"},
        {"name": "Backwaters", "icon": "bi-tsunami", "desc": "Serene houseboat trails in Alappuzha & Kumarakom"},
        {"name": "Waterfalls", "icon": "bi-moisture", "desc": "Cascades of Athirappilly, Meenmutty & Palaruvi"},
        {"name": "Wildlife Sanctuaries", "icon": "bi-shield-check", "desc": "Periyar, Silent Valley & Wayanad reserves"},
        {"name": "Heritage & Culture", "icon": "bi-bank", "desc": "Fort Kochi, Kathakali & royal palaces"}
    ]
    return render(request, 'home.html', {
        'districts': districts,
        'categories': categories,
    })

def about(request):
    """About Kerala Smart Tourism."""
    return render(request, 'about.html')
