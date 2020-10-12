from codustry.models.craftsman import AllCraftsmanTypes
from codustry.models.craftsman import AuthorizeLevel
from codustry.protocals.inactive import make_inactive


@situation(who=AllCraftsmanTypes, when=AllTime, where=AllPlaces, overwrite_by=AuthorizeLevel.TeamLead)
def reply(craftsman: AllCraftsmanTypes):
    communications = [k for k in craftsman.karma if k.type is 'Communication']
    for c in communications:
        if c.channel == 'chat' and c.response_time > 1 * day \
                or c.channel == 'call' and c.response_time > 1 * day:
            craftsman.inactive = True
            make_inactive(craftsman)

