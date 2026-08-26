from django.shortcuts import render, redirect
# user
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Task, Category, Subtask
from reporting.models import CompletedTask, TaskHistory
from django.utils import timezone
import time
from .forms import CategoryForm, NewTaskForm

@login_required
def index(request):
    # todos in reverse order
    todos = Task.objects.filter(completed=False, in_progress=False, user=request.user).order_by('-created_at')
    completed = Task.objects.filter(completed=True, user=request.user).order_by('-completed_at').filter(completed_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0))
    in_progress = Task.objects.filter(in_progress=True, user=request.user)
    categories = Category.objects.filter(user=request.user)
    context = {
        "tasks_todo": todos,
        "tasks_completed": completed,
        "tasks_in_progress": in_progress,
        "categories": categories,
        "task_form": NewTaskForm(),
        "category_form": CategoryForm()
    }
    return render(request, 'dashboard/tasks_list.html', context)

@login_required
def in_progress(request, id):
    task = Task.objects.get(id=id, user=request.user)
    # A single click now moves the task only one step; rollback is always available.
    task.in_progress = True
    task.completed = False
    task.completed_at = None
    task.save()
    TaskHistory.objects.create(task=task, user=request.user, status='In Progress', action='Moved to In Progress')
    return redirect('dashboard:index')

@login_required
def undo_progress(request, id):
    task = Task.objects.get(id=id, user=request.user)
    task.in_progress = False
    task.completed = False
    task.completed_at = None
    task.save()
    TaskHistory.objects.create(task=task, user=request.user, status='To Do', action='Rolled back to To Do')
    return redirect('dashboard:index')

@login_required
def completed(request, id):
    try:
        task = Task.objects.get(id=id, user=request.user)
        task.completed = True
        task.completed_at = timezone.now()
        task.in_progress = False
        task.save()
        TaskHistory.objects.create(task=task, user=request.user, status='Completed', action='Marked as Completed')
        CompletedTask.objects.create(
            title=task.title,
            description=task.description,
            created_at=task.created_at,
            completed_at=task.completed_at,
            category=task.category.name if task.category else "Others",
            user=task.user,
            status="Completed",
            action="Task completed",
        )
        return redirect('dashboard:index')
    except Task.DoesNotExist:
        return HttpResponseNotFound("Task not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponseServerError("An error occurred while processing your request. Please try again later.")

@login_required
def task_detail(request, id):
    task = Task.objects.get(id=id, user=request.user)
    subtasks = task.subtasks.all()
    history = TaskHistory.objects.filter(
        user=request.user, task=task
    ).order_by('-changed_at')
    all_subtasks_completed = subtasks.exists() and not subtasks.filter(completed=False).exists()

    return render(request, 'dashboard/task_detail.html', {
        'task': task,
        'subtasks': subtasks,
        'history': history,
        'all_subtasks_completed': all_subtasks_completed,
    })

@login_required
def add_subtask(request, id):
    task = Task.objects.get(id=id, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            Subtask.objects.create(task=task, title=title)
    return redirect('dashboard:task_detail', id=task.id)

@login_required
def toggle_subtask(request, id, subtask_id):
    task = Task.objects.get(id=id, user=request.user)
    subtask = Subtask.objects.get(id=subtask_id, task=task)
    if request.method == 'POST':
        subtask.completed = not subtask.completed
        subtask.save(update_fields=['completed'])
    return redirect('dashboard:task_detail', id=task.id)

@login_required
def create(request):
    if request.method == 'POST':
        form = NewTaskForm(request.POST)
        if form.is_valid():
            # Create a new task
            task = form.save(commit=False)
            task.user = request.user
            task.category = Category.objects.get(id=request.POST.get('category'))
            task.save()
        
        return redirect('dashboard:index')
    else:
        form = NewTaskForm()
    return render(request, 'dashboard/create_task.html', {'task_form': form})

@login_required
def update(request, id):
    task = Task.objects.get(id=id, user=request.user)
    task.completed = not task.completed
    task.save()
    return render(request, 'dashboard/tasks_list.html')

@login_required
def delete(request, id):
    task = Task.objects.get(id=id, user=request.user)
    task.delete()
    return redirect('dashboard:index')

@login_required
def reset_all(request):
    if request.method == 'POST':
        Task.objects.filter(user=request.user).delete()
        CompletedTask.objects.filter(user=request.user).delete()
    return redirect('dashboard:index')

@login_required
def new_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
        return redirect('dashboard:index')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/create_category.html', {'category_form': form})

@staff_member_required
def clear_categories(request):
    Category.objects.all().delete()
    return redirect('dashboard:index')