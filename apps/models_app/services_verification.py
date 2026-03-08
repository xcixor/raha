from .models import ModelProfile

class VerificationService:
    @staticmethod
    def verify_profile(profile_id):
        """
        Marks a profile as verified and active.
        """
        profile = ModelProfile.objects.get(id=profile_id)
        profile.is_verified = True
        profile.is_active = True
        profile.save()
        return profile

    @staticmethod
    def reject_profile(profile_id):
        """
        Marks a profile as unverified and inactive.
        """
        profile = ModelProfile.objects.get(id=profile_id)
        profile.is_verified = False
        profile.is_active = False
        profile.save()
        return profile
