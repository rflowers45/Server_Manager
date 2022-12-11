import bcrypt
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password
from .models import Course
from .models import Group, TestUser
from user.models import AppUser
from .forms import GroupForm, TestUserForm, StudentLoginForm
from django.contrib import messages
from random import *
import string
import hashlib
import base64
import uuid


# Create your views here.
def createGroup(request, id):
    course = Course.objects.get(pk=id)
    user = course.user
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            try:
                instance = form.save(commit=False)
                instance.course = course;
                instance.save()
                return redirect('profHome', user.id)
            except:
                pass
    else:
        form = GroupForm()
        return render(request, 'group/createGroup.html', {'form': form, 'course': course})


def groupDetail(request, id):
    group = get_object_or_404(Group, pk=id)
    groupId = id
    list_credentials = TestUser.objects.filter(group__pk=id)
    context = {"group": group, "testUser": list_credentials, "groupId": groupId}
    return render(request, "group/groupDetail.html", context=context)


def destroyGroup(request, id):
    group = Group.objects.get(id=id)
    course = group.course
    user = course.user
    group.delete()
    return redirect('profHome', user.id)


def editGroup(request, id):
    group = get_object_or_404(Group, pk=id)
    return render(request, "group/editGroup.html", {"group": group})


def updateGroup(request, id):
    group = Group.objects.get(id=id)
    course = group.user
    user = course.user

    form = GroupForm(request.POST, instance=group)
    if form.is_valid():
        form.save()

    return redirect('profHome', user.id)
    return render(request, 'group/editGroup.html', {'group': group})


def generateUser(request, id):
    group = Group.objects.get(pk=id)
    char = string.ascii_letters + string.punctuation + string.digits
    if request.method == "POST":
        form = TestUserForm(request.POST)
        if form.is_valid():
            try:
                instance = form.save(commit=False)
                username = instance.firstname + instance.lastname
                instance.username = instance.firstname + instance.lastname
                password = "".join(choice(char) for x in range(randint(5, 16)))
                salt = bcrypt.gensalt()
                encoded = password.encode('utf8')
                hashpass = bcrypt.hashpw(encoded, salt)
                hashpass2 = hashpass.decode('utf8')
                instance.password = hashpass2
                instance.group = group
                instance.save()
                context = {"pass": password, "user": username}
                context['group'] = group
                return render(request, "group/displayPassword.html", context=context)
            except:
                pass
    else:
        form = TestUserForm()
        return render(request, 'group/createCredentials.html', {'form': form, 'group': group})

def deleteCredentials(request, id):
  user = TestUser.objects.get(id=id)
  user.delete()
  return redirect('groupDetail', user.group.id)


#This is the custom login class for students
def studentLogin(request):
    if request.method == "POST":
        form = StudentLoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = TestUser.objects.get(username=username)
        userBytes = request.POST['password'].encode('utf-8')
        hash = user.password.encode('utf-8')
        result = bcrypt.checkpw(password.encode(), hash)
        print(result)
        if result is True:
            return redirect('studentHome', user.id)
        else:
            messages.error(request, 'Username/Password incorrect!')
    else:
        form = StudentLoginForm(request.POST)
        return render(request, 'group/studentlogin.html', {'form': form})
