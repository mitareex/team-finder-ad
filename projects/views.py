from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


PROJECTS_PER_PAGE = 12
OPEN = 'open'
CLOSED = 'closed'
OK = 'ok'
ERROR = 'error'
FORBIDDEN = 403
BAD_REQUEST = 400
ACCESS_DENIED = 'Доступ запрещен'
AUTHOR_LEAVE_DENIED = 'Автор не может покинуть свой проект'


def _paginate_queryset(request, queryset):
    paginator = Paginator(queryset, PROJECTS_PER_PAGE)
    page_number = request.GET.get('page')

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def project_list(request):
    projects_queryset = Project.objects.select_related('owner').all()
    projects = _paginate_queryset(request, projects_queryset)

    return render(request, 'projects/project_list.html', {'projects': projects})


def project_details(request, project_id):
    project_instance = get_object_or_404(
        Project.objects.select_related('owner'),
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
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project_instance = form.save(commit=False)
            project_instance.owner = request.user
            project_instance.save()
            project_instance.participants.add(request.user)
            return redirect('projects:project-details', project_id=project_instance.id)
    else:
        form = ProjectForm()

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

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project_instance)
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

    if project_instance.owner == request.user and project_instance.status == OPEN:
        project_instance.status = CLOSED
        project_instance.save()
        return JsonResponse({
            'status': OK,
            'project_status': CLOSED
        })

    return JsonResponse({'status': ERROR, 'message': ACCESS_DENIED}, status=FORBIDDEN)


@login_required
@require_POST
def toggle_participate(request, project_id):
    project_instance = get_object_or_404(Project, id=project_id)
    user = request.user

    if project_instance.owner == request.user:
        return JsonResponse({'status': ERROR, 'message': AUTHOR_LEAVE_DENIED}, status=BAD_REQUEST)

    if project_instance.participants.filter(id=user.id).exists():
        project_instance.participants.remove(user)
        participant = False
    else:
        project_instance.participants.add(user)
        participant = True

    return JsonResponse({'status': OK, 'participant': participant})


@login_required
def favorite_projects(request):
    projects_queryset = request.user.favorites.select_related('owner').all()
    projects = _paginate_queryset(request, projects_queryset)

    return render(request, 'projects/favorite_projects.html', {'projects': projects})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project_instance = get_object_or_404(Project, id=project_id)
    user = request.user

    if user.favorites.filter(id=project_instance.id).exists():
        user.favorites.remove(project_instance)
        favorited = False
    else:
        user.favorites.add(project_instance)
        favorited = True

    return JsonResponse({'status': OK, 'favorited': favorited})
