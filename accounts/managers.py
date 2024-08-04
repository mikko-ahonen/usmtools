from django.contrib.auth.base_user import BaseUserManager

class ProfileManager(BaseUserManager):
    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('i_like').prefetch_related('liked_by')
        return qs
