from django.contrib.auth import update_session_auth_hash, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import ChangePasswordForm, ProfileEditForm, RegisterForm, LoginForm
from projects.models import Project
from projects.services import paginate_queryset

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('projects:project_list')

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user_instance = form.save()
        login(request, user_instance)
        return redirect('projects:project_list')

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('projects:project_list')

    form = LoginForm(request.POST or None)
    if form.is_valid():
        user_instance = form.cleaned_data.get('user')
        if user_instance is not None:
            login(request, user_instance)
            return redirect('projects:project_list')

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('projects:project_list')


@login_required
def edit_profile_view(request):
    user_instance = request.user

    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=user_instance)
    if form.is_valid():
        form.save()
        return redirect('users:user_details', user_id=user_instance.id)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    user_instance = request.user

    form = ChangePasswordForm(user=user_instance, data=request.POST or None)
    if form.is_valid():
        user_instance.set_password(form.cleaned_data['new_password1'])
        user_instance.save()
        update_session_auth_hash(request, user_instance)
        return redirect('users:user_details', user_id=user_instance.id)

    return render(request, 'users/change_password.html', {'form': form})


def user_details_view(request, user_id):
    user_instance = get_object_or_404(User, id=user_id)
    return render(request, 'users/user-details.html', {'user': user_instance})


def users_list_view(request):
    users_queryset = User.objects.all().order_by('id')

    current_user = request.user
    active_filter = request.GET.get('filter')

    if current_user.is_authenticated:
        if active_filter:
            if active_filter == 'owners-of-favorite-projects':
                author_ids = current_user.favorites.values_list('owner_id', flat=True)
                users_queryset = users_queryset.filter(id__in=author_ids)
            elif active_filter == 'owners-of-participating-projects':
                author_ids = Project.objects.filter(participants=current_user).values_list(
                    'owner_id',
                    flat=True
                )
                users_queryset = users_queryset.filter(id__in=author_ids)
            elif active_filter == 'interested-in-my-projects':
                users_queryset = users_queryset.filter(favorites__owner=current_user)
            elif active_filter == 'participants-of-my-projects':
                if request.user.is_authenticated:
                    users_queryset = users_queryset.filter(
                        participated_projects__owner=request.user
                    ).exclude(id=request.user.id)
                else:
                    users_queryset = users_queryset.none()

            users_queryset = users_queryset.distinct()

    participants = paginate_queryset(request, users_queryset)

    context = {
        'participants': participants,
        'active_filter': active_filter
    }
    return render(request, 'users/participants.html', context)
