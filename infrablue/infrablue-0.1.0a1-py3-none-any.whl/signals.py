def add_preference_permissions(sender, instance, **kwargs) -> None:
    from guardian.shortcuts import assign_perm

    print(sender, instance)

    assign_perm("auth.change_user", user_or_group=instance, obj=instance)
    assign_perm("auth.delete_user", user_or_group=instance, obj=instance)