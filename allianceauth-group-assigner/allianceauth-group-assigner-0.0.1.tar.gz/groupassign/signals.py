from django.dispatch import receiver

from django.db.models.signals import pre_save
from django.core.exceptions import ObjectDoesNotExist

from allianceauth.authentication.models import UserProfile
from .models import StateGroupBinding

from allianceauth.services.hooks import get_extension_logger
logger = get_extension_logger(__name__)

@receiver(pre_save, sender=UserProfile)
def state_change(sender, instance, raw, using, update_fields, **kwargs):
    try:
        if instance.pk:
            old_instance = UserProfile.objects.get(pk=instance.pk)
            if old_instance.state != instance.state:
                logger.debug("State changed: Checking for Groups")
                group_lists = StateGroupBinding.objects.get(state=instance.state).groups.all()
                for grp in group_lists:
                    if grp not in instance.user.groups.all():
                        instance.user.groups.add(grp)
    except ObjectDoesNotExist as e:
        pass # no config for this state so skip.
    except Exception as e:
        logger.error(e)
        pass  # shits fucked... Don't worry about it...  Sometimes you just have to lick the stamp and send it.
