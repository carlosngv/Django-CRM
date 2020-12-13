'''
    Signals allows us to associate an action to an event. In this case,
    thanks to this, when we create a new user, automatically we are creating
    the customer too. This links the new user to the new customer/profile.
    
    Decoraters can me use to instead of the post_save.connect() method.
    Only place de @receiver(post_save, sender=User) decorator above
    the function.
'''

from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer


def customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='customer')
        instance.groups.add(group)
        Customer.objects.create(
            user=instance,
            name=instance.username
        )
        print('Profile created!')


post_save.connect(customer_profile, sender=User)
