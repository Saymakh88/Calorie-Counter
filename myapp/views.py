from django.shortcuts import render,redirect
from .models import Food, Consume
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Create your views here.
def index(request):
    if request.method =="POST":
        food_consumed=request.POST['food_consumed']
        consume=Food.objects.get(name=food_consumed)
        user=request.user
        consume=Consume(user=user,food_consumed=consume)
        consume.save()
        foods=Food.objects.all()

    else:
        foods=Food.objects.all()
    consumed_food=Consume.objects.filter(user=request.user)
    return render(request,'myapp/index.html',{'foods':foods,'consumed_food':consumed_food})


def delete_consume(request,id):
    consumed_food=Consume.objects.get(id=id)
    if request.method=='POST':
        consumed_food.delete()
        return redirect('/')
    return render(request,'myapp/delete.html')


def profile_view(request):
    return render(request, 'myapp/profile.html')

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})




