from django.shortcuts import render
from .models import HousePrice

def house_list(request):
    houses = HousePrice.objects.all()

    return render(request, 'real_estate/house_list.html', {'houses': houses})

