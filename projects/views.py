from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .constants import (
    OPEN_STATUS,
    CLOSED_STATUS,
    API_STATUS_OK,
    API_STATUS_ERROR,
    HTTP_FORBIDDEN,
    HTTP_BAD_REQUEST,
    ACCESS_DENIED_MSG,
    AUTHOR_LEAVE_DENIED_MSG
)
from .forms import ProjectForm
from .models import Project
from .services import paginate_queryset


def project_list(request):
    projects_queryset = Project.objects.select_related(
        'owner').prefetch_related('participants').all()
    projects = paginate_queryset(request, projects_queryset)
    return render(request, 'projects/project_list.html', {'projects': projects})


def project_details(request, project_id):
    project_instance = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        id=project_id
    )

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = request.user.favorites.filter(id=project_instance.id).exists()

    context = {
        'project': project_instance,
        'is_favorite': is_favorite
    }

    return render(request, 'projects/project-details.html', context)


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project_instance = form.save(commit=False)
        project_instance.owner = request.user
        project_instance.save()
        project_instance.participants.add(request.user)
        return redirect('projects:project-details', project_id=project_instance.id)

    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'projects/create-project.html', context)


@login_required
def edit_project(request, project_id):
    project_instance = get_object_or_404(Project, id=project_id)

    if project_instance.owner != request.user:
        return redirect('projects:project_details', project_id=project_instance.id)

    form = ProjectForm(request.POST or None, instance=project_instance)

    if form.is_valid():
        form.save()
        return redirect('projects:project-details', project_id=project_instance.id)

    else:
        form = ProjectForm(instance=project_instance)

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'projects/create-project.html', context)


@login_required
@require_POST
def complete_project(request, project_id):
    project_instance = get_object_or_404(Project, id=project_id)

    if project_instance.owner == request.user and project_instance.status == OPEN_STATUS:
        project_instance.status = CLOSED_STATUS
        project_instance.save()
        return JsonResponse({
            'status': API_STATUS_OK,
            'project_status': CLOSED_STATUS
        })

    return JsonResponse({
        'status': API_STATUS_ERROR,
        'message': ACCESS_DENIED_MSG},
        status=HTTP_FORBIDDEN
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project_instance = get_object_or_404(Project, id=project_id)
    user = request.user

    if project_instance.owner == request.user:
        return JsonResponse({
            'status': API_STATUS_ERROR, 'message': AUTHOR_LEAVE_DENIED_MSG},
            status=HTTP_BAD_REQUEST
        )

    if is_participant := project_instance.participants.filter(id=user.id).exists():
        project_instance.participants.remove(user)
    else:
        project_instance.participants.add(user)

    return JsonResponse({'status': API_STATUS_OK, 'participant': not is_participant})


@login_required
def favorite_projects(request):
    projects_queryset = request.user.favorites.select_related(
        'owner').prefetch_related('participants').all()
    projects = paginate_queryset(request, projects_queryset)

    return render(request, 'projects/favorite_projects.html', {'projects': projects})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project_instance = get_object_or_404(Project, id=project_id)
    user = request.user

    if is_favorited := user.favorites.filter(id=project_instance.id).exists():
        user.favorites.remove(project_instance)
    else:
        user.favorites.add(project_instance)

    return JsonResponse({'status': API_STATUS_OK, 'favorited': not is_favorited})
