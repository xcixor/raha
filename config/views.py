from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            return redirect('models:profile_detail')
        return redirect('models:onboarding')
    return redirect('accounts:register')
