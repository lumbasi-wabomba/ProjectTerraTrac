from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class TerratracUser(AbstractUser):
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_num = models.CharField(max_length=15, blank=True, null=True)
    points = models.PositiveIntegerField(default=0)
    badges = models.ManyToManyField('Badge', blank=True, db_index=True)

    def __str__(self):
        return self.username

class Badge(models.Model):
    BADGE_CHOICES = [
        ('Emerald Guardian', 'Emerald Guardian'),
        ('Sapphire Scout', 'Sapphire Scout'),
        ('Ruby Defender', 'Ruby Defender'),
        ('Diamond Champion', 'Diamond Champion'),
        ('Amethyst Advocate', 'Amethyst Advocate'),
        ('Pearl Pioneer', 'Pearl Pioneer'),
    ]
    name = models.CharField(max_length=100, choices=BADGE_CHOICES)
    description = models.TextField(max_length=300)

    def __str__(self):
        return f"{self.username} {self.first_name}"
    
class ForestArea(models.Model):
    name = models.CharField(max_length=250)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(max_length=500)
    last_ndvi = models.FloatField(default=0.0)
    last_date_checked = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name} {self.latitude} {self.longitude}"
    
class NDVIRecord(models.Model):
    forest_area = models.ForeignKey(ForestArea, on_delete=models.CASCADE, related_name='forest_NDVI_Records')
    ndvi_values = models.FloatField()
    image_taken_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.forest_area} {self.ndvi_values}"

class Alert(models.Model):
    forest_area = models.ForeignKey(ForestArea, on_delete=models.CASCADE, related_name='forest_alerts')
    ALERT_CHOICES = [
        ('Afforestation', 'afforestation'),
        ('Deforestation', 'deforestation')
    ]
    alert_type = models.CharField(max_length=50, choices=ALERT_CHOICES, db_index=True)
    change_value = models.FloatField()
    triggered_on = models.DateField(auto_now_add=True)
    STATUS_CHOICES=[
        ('Verified','Verified'),
        ('Pending', 'Pending'),
        ('Rejected','Rejected')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)

    def __str__(self):
        return f"{self.forest_area} {self.alert_type} {self.change_value}"
    
class CommunityReport(models.Model):
    reported_by = models.ForeignKey(TerratracUser, on_delete=models.CASCADE, related_name='user_issued_reports')
    forest_area = models.ForeignKey(ForestArea, on_delete=models.CASCADE, related_name='forests', null=True)
    image = models.URLField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(max_length=500)
    submitted_on = models.DateField(auto_now_add=True)
    linked_alerts = models.ManyToManyField('Alert', related_name='linked_reports')

    def __str__(self):
        return f"{self.reported_by} {self.longitude} {self.latitude}"
    
class Verification(models.Model):
    verified_by = models.ForeignKey(TerratracUser, on_delete=models.CASCADE, related_name='user_verifications')
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    notes = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.verified_by} {self.timestamp}"
    