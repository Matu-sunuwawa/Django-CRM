from django.db import models
# from django.contrib.auth import get_user_model

# after commited change in database is "post_save"
from django.db.models.signals import post_save, pre_save

# we import default AbstractUser model inorder to customize User...that is recommendation.
from django.contrib.auth.models import AbstractUser

# User = get_user_model()



# "ForeignKey" allows to create many "Agents for one user"....so it looks like Foreign key is just OneToMany relationship
# i.e, class Agent(models.Model):
#           user = models.ForeignKey(User, on_delete=models.CASCADE)

# there are also other more better way...customiz User from scratch.
class User(AbstractUser):
    # identify user types...whether it is organizer or agent
    is_organizer = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# we use f_name,l_name cuz it doesn't required to logged in
class Lead(models.Model):

    # SOURCE_CHOICES = (
    #     ('YouTube', 'YouTube'),
    #     ('Google', 'Google'),
    #     ('Newsletter', 'Newsletter')
    # )

    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField(default=0)
    # agent = models.ForeignKey("Agent", on_delete=models.CASCADE)
    
    # we do not want organizations to see other organizations "leads"...so filter by using organization...check on "LeadListView" in views.py
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    agent = models.ForeignKey("Agent",null=True, blank=True, on_delete=models.SET_NULL)
    # "related_name="leads" is the name given to relationship of "Lead" and "Category"...and it used in "CategoryDetailView"...
    # and more conventional way to give name for rlated_name is declare name by making plural the model name..."Lead"==>"leads","Hello"==>"hellos"
    category = models.ForeignKey("Category", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)

    # phoned = models.BooleanField(default=False)
    # source = models.CharField(choices=SOURCE_CHOICES, max_length=100)

    # profile_picture = models.ImageField(blank=True, null=True)
    # special_files = models.FileField(blank=True, null=True)

    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Agent(models.Model):
    # this one represents "Agent"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
# we comment out cuz it will inherit from "Abstractmodel"
    # first_name = models.CharField(max_length=20)
    # last_name = models.CharField(max_length=20)
    # lead = models.ForeignKey("Lead", on_delete=models.CASCADE)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    # This one called ORM(object relational mapper)
    def __str__(self):
        return self.user.email
    

class Category(models.Model):
    name = models.CharField(max_length=30) # New, Contacted, Converted, Unconverted
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

# Django Signal
    # its all about triggering the "event"...and based on that it makes us able to create d/t objects like "UserProfile"
    # **kwargs --> capture any other arguments if they are any...
def post_user_created_signal(sender, instance, created, **kwargs):
    print(instance, created)
    if created:
        UserProfile.objects.create(user=instance)

# When in the django admin save button "clicked" this will be run...
post_save.connect(post_user_created_signal, sender=User)