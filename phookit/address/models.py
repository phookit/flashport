from django.conf import settings
from django.db import models

from geopy.geocoders import GoogleV3 as GoogleMaps
from geopy.exc import GeocoderQueryError


class Address(models.Model):
    street1 = models.CharField(max_length=128, help_text="")
    street2 = models.CharField(max_length=128, null=True, blank=True, help_text="")
    area = models.CharField(max_length=128, null=True, blank=True, help_text="")
    city = models.CharField(max_length=128, null=True, blank=True, help_text="City")
    country = models.CharField(max_length=128, null=True, blank=True, help_text="Country")
    code = models.CharField(max_length=128, null=True, blank=True, help_text="ZIP/post code")
    mappable_location = models.CharField(max_length=128, null=True, blank=True, help_text="")
    lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, verbose_name="Latitude", help_text="Calculated automatically if mappable location is set.")
    lon = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, verbose_name="Longitude", help_text="Calculated automatically if mappable location is set.")


    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
    

    def __unicode__(self):
        return "%s, %s" % ( self.street1, self.code )


    def clean(self):
        super(Address, self).clean()
        
        if self.lat and not self.lon:
            raise ValidationError("Longitude required if specifying latitude.")
        
        if self.lon and not self.lat:
            raise ValidationError("Latitude required if specifying longitude.")
        
        if not (self.lat and self.lon) and not self.mappable_location:
            self.mappable_location = self.street1
            if self.street2:
                self.mappable_location += ", %s" % self.street2
            if self.area:
                self.mappable_location += ", %s" % self.area
            if self.city:
                self.mappable_location += ", %s" % self.city
            if self.country:
                self.mappable_location += ", %s" % self.country
            if self.code:
                self.mappable_location += ", %s" % self.code
        if self.mappable_location: #location should always override lat/long if set
            g = GoogleMaps(domain=settings.GEOCODERS_GOOGLE_MAPS_DOMAIN)
            try:
                address, (lat, lon) = g.geocode(self.mappable_location.encode('utf-8'))
            except GeocoderQueryError as e:
                raise ValidationError("The mappable location you specified could not be found on {service}: \"{error}\" Try changing the mappable location, removing any business names, or leaving mappable location blank and using coordinates from getlatlon.com.".format(service="Google Maps", error=e.message))
            except TypeError as e:
                raise ValidationError("The mappable location you specified could not be found on {service}: \"{error}\" Try changing the mappable location, removing any business names, or leaving mappable location blank and using coordinates from getlatlon.com.".format(service="Google Maps", error=e.message))
            except ValueError as e:
                raise ValidationError("The mappable location you specified could not be found on {service}: \"{error}\" Try changing the mappable location, removing any business names, or leaving mappable location blank and using coordinates from getlatlon.com.".format(service="Google Maps", error=e.message))
            self.mappable_location = address
            self.lat = lat
            self.lon = lon
