from django.db import models

# generated
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from django.db.models import Q

# Create your models here.


class Contact(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField()
    phonenumber=models.CharField(max_length=13)
    description=models.TextField()
    
    def __str__(self):
        return self.email
    
class Enrollment(models.Model):        
    FullName=models.CharField(max_length=30)
    Email=models.EmailField()
    Gender=models.CharField(max_length=30)
    PhoneNumber=models.CharField(max_length=13)
    DOB=models.CharField(max_length=55)
    SelectMembershipplan=models.CharField(max_length=250)
    SelectTrainer=models.CharField(max_length=50)
    Reference=models.CharField(max_length=50)
    Address=models.TextField()
    paymentStatus=models.CharField(max_length=65,blank=True,null=True)
    Price=models.IntegerField(blank=True,null=True)
    DueDate=models.DateTimeField(blank=True,null=True)
    timeStamp=models.DateTimeField(auto_now_add=True,blank=True,)

    def __str__(self):
        return self.FullName
    
    
class Trainer(models.Model):
    name=models.CharField(max_length=55)
    username=models.CharField(max_length=55,blank=True,null=True)
    gender=models.CharField(max_length=25)
    phone=models.CharField(max_length=25)
    salary=models.IntegerField()
    timeStamp=models.DateTimeField(auto_now_add=True,blank=True)
    def __str__(self):
        return self.name
    
class MembershipPlan(models.Model):
    plan = models.CharField(max_length=185)
    price = models.IntegerField()
    duration_days = models.IntegerField(default=30)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.plan
    
class Attendance(models.Model):
    Selectdate=models.DateTimeField(auto_now_add=True)
    phonenumber=models.CharField(max_length=15)
    Login=models.CharField(max_length=200)
    Logout=models.CharField(max_length=200)
    SelectWorkout=models.CharField(max_length=200)
    TrainedBy=models.CharField(max_length=200)
    def __int__(self):
        return self.id
    
class Gallery(models.Model):
    title=models.CharField(max_length=100)
    img=models.ImageField(upload_to='gallery')
    timeStamp=models.DateTimeField(auto_now_add=True,blank=True)
    def __int__(self):
        return self.id
    
    
# -----generated----
# 1. Paystack Configuration (Singleton)
class PaystackConfiguration(models.Model):
    name = models.CharField(max_length=100, default="Paystack Settings")
    public_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Paystack Configuration"

    #ensures only one instance exists
    def save(self, *args, **kwargs):
        if not self.pk and PaystackConfiguration.objects.exists():
            return 
        return super().save(*args, **kwargs)

# 2. Membership Tracking
class UserMembership(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    plan_name = models.CharField(max_length=100, null=True, blank=True)
    paystack_ref = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_frozen = models.BooleanField(default=False)
    remaining_days_at_freeze = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def has_expired(self):
        if not self.expiry_date:
            return True

        if self.is_frozen:
            return False

        if timezone.now() > self.expiry_date:
            if self.is_active:
                self.is_active = False
                self.save(update_fields=["is_active"])
            return True

        return False
    
# class UserMembership(models.Model):
#     # These MUST match the names in your admin's list_display
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     plan_name = models.CharField(max_length=100, default="Basic")
#     expiry_date = models.DateTimeField(default=timezone.now)
    
#     # Other necessary fields
#     is_active = models.BooleanField(default=True)
#     paystack_ref = models.CharField(max_length=100, unique=True, null=True, blank=True)
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

#     def __str__(self):
#         return f"{self.user.username} - {self.plan_name}"

#     @property
#     def has_expired(self):
#         return timezone.now() > self.expiry_date

# 3. Workout PDFs
class WorkoutPlan(models.Model):
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='workouts/')
    membership_level = models.CharField(max_length=20, choices=[('BASIC', 'Basic'), ('ELITE', 'Elite')])
    
    def __str__(self):
        return self.title
    
#4. Services Section


class Service(models.Model):

    name = models.CharField(max_length=150)

    description = models.TextField()

    image = models.ImageField(upload_to="services/", blank=True, null=True)

    price = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return self.name
    


#This prevents:
#Even if your logic fails — database will NOT allow two active memberships.
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=['user'],
            condition=Q(is_active=True),
            name='only_one_active_membership_per_user'
        )
    ]