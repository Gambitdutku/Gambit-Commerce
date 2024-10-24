from django.apps import AppConfig
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Address, District, Area, Neighborhood, City
import random

import string
import requests  # API istekleri için requests modülünü ekleyin

class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'


class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['user', 'first_name', 'last_name', 'email', 'phone_number', 'birth_date']


class AddressAdminForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['user_profile', 'city', 'district', 'area', 'neighborhood', 'address']

    def __init__(self, *args, **kwargs):
        super(AddressAdminForm, self).__init__(*args, **kwargs)
        self.fields['district'].queryset = District.objects.none()
        self.fields['area'].queryset = Area.objects.none()
        self.fields['neighborhood'].queryset = Neighborhood.objects.none()

        if 'city' in self.data:
            try:
                city_id = int(self.data.get('city'))
                # API'den ilçe verilerini al
                self.fields['district'].queryset = self.get_districts(city_id)

                if 'district' in self.data:
                    district_id = int(self.data.get('district'))
                    # API'den alan verilerini al
                    self.fields['area'].queryset = self.get_areas(district_id)

                    if 'area' in self.data:
                        area_id = int(self.data.get('area'))
                        # API'den mahalle verilerini al
                        self.fields['neighborhood'].queryset = self.get_neighborhoods(area_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            # Düzenleme modunda mevcut örneğe göre doldur
            self.fields['district'].queryset = self.get_districts(self.instance.city.id)
            self.fields['area'].queryset = self.get_areas(self.instance.district.id)
            self.fields['neighborhood'].queryset = self.get_neighborhoods(self.instance.area.id)

    def get_districts(self, city_id):
        """API'den ilçeleri al."""
        response = requests.get(f'http://127.0.0.1:8000/api/cities/{city_id}/districts/?format=json')
        if response.status_code == 200:
            districts = response.json()
            return District.objects.filter(id__in=[district['id'] for district in districts])
        return District.objects.none()

    def get_areas(self, district_id):
        """API'den alanları al."""
        response = requests.get(f'http://127.0.0.1:8000/api/districts/{district_id}/areas/?format=json')
        if response.status_code == 200:
            areas = response.json()
            return Area.objects.filter(id__in=[area['id'] for area in areas])
        return Area.objects.none()

    def get_neighborhoods(self, area_id):
        """API'den mahalleleri al."""
        response = requests.get(f'http://127.0.0.1:8000/api/areas/{area_id}/neighborhoods/?format=json')
        if response.status_code == 200:
            neighborhoods = response.json()
            return Neighborhood.objects.filter(id__in=[neighborhood['id'] for neighborhood in neighborhoods])
        return Neighborhood.objects.none()


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=15)
    birth_date = forms.DateField()

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']

    def generate_random_username(self, length=8):
        """Generate a random username."""
        characters = string.ascii_letters + string.digits
        username = ''.join(random.choice(characters) for _ in range(length))
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        # Generate a random username and check for uniqueness
        while True:
            user.username = self.generate_random_username()
            if not User.objects.filter(username=user.username).exists():
                break

        if commit:
            user.save()
            # Create UserProfile instance with additional fields
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                birth_date=self.cleaned_data['birth_date'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email']
            )
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'birth_date']
