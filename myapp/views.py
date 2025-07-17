from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.http import HttpResponse
from datetime import date, datetime
import matplotlib.pyplot as plt
from io import BytesIO
from .models import Food, Consume
from .utils import run_query
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404


@login_required
def index(request):
    selected_date = request.GET.get('date')
    if selected_date:
        date_obj = parse_date(selected_date)
        consumed_food = Consume.objects.filter(user=request.user, timestamp__date=date_obj)
    else:
        selected_date = date.today().isoformat()
        date_obj = date.today()
        consumed_food = Consume.objects.filter(user=request.user, timestamp__date=date.today())

    if request.method =="POST":
        food_name=request.POST['food_consumed']
        food_item=Food.objects.get(name=food_name)
        Consume.objects.create(user=request.user, food_consumed=food_item)
        return redirect(f"{request.path}?date={selected_date}") 


    foods=Food.objects.all()
    consumed_food = Consume.objects.filter(user=request.user)


# ✅ 1. SQL: Average calories consumed
    avg_query = """
        SELECT AVG(f.calories)
        FROM myapp_consume c
        JOIN myapp_food f ON c.food_consumed_id = f.id
        WHERE c.user_id = %s AND DATE(c.timestamp) = %s
    """
    avg_calories = run_query(avg_query,[request.user.id, selected_date])[0][0] or 0

# ✅ 2. SQL: Most frequently eaten food
    freq_query = """
        SELECT f.name, COUNT(*) as freq
        FROM myapp_consume c
        JOIN myapp_food f ON c.food_consumed_id = f.id
        WHERE c.user_id = %s AND DATE(c.timestamp) = %s
        GROUP BY f.name
        ORDER BY freq DESC
        LIMIT 1
    """ 


    most_eaten_result = run_query(freq_query,[request.user.id, selected_date])
    most_eaten_food = most_eaten_result[0][0] if most_eaten_result else "N/A"  

    return render(request, 'myapp/index.html', {
        'foods': foods,
        'consumed_food': consumed_food,
        'avg_calories': round(avg_calories, 2),
        'most_eaten_food': most_eaten_food,
        'selected_date': selected_date,
        'timestamp': datetime.now().timestamp()
    })
@login_required
def calorie_trend_plot(request):
    trend_query = """
        SELECT DATE(c.timestamp) AS date, SUM(f.calories) AS total_calories
        FROM myapp_consume c
        JOIN myapp_food f ON c.food_consumed_id = f.id
        WHERE c.user_id = %s
        GROUP BY DATE(c.timestamp)
        ORDER BY DATE(c.timestamp) DESC
        LIMIT 7
    """
    trend_data = run_query(trend_query,[request.user.id])

    dates = [str(row[0]) for row in trend_data][::-1]
    calories = [row[1] for row in trend_data][::-1]

    fig, ax = plt.subplots()
    ax.plot(dates, calories, marker='o', color='green')
    ax.set_title('Weekly Calorie Trend')
    ax.set_ylabel('Calories')
    ax.set_xlabel('Date')
    ax.grid(True)

    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type='image/png')

@login_required
def macronutrient_pie_chart(request):
    selected_date = request.GET.get('date')
    if selected_date:

        consumed = Consume.objects.filter(user=request.user, timestamp__date=selected_date).select_related('food_consumed')
    else:
        consumed = Consume.objects.filter(user=request.user, timestamp__date=date.today()).select_related('food_consumed')

    total_carbs = sum(item.food_consumed.carbs for item in consumed)
    total_protein = sum(item.food_consumed.protein for item in consumed)
    total_fats = sum(item.food_consumed.fats for item in consumed)

    labels = ['Carbs', 'Protein', 'Fats']
    values = [total_carbs, total_protein, total_fats]
    colors = ['#4CAF50', '#FF5733', '#FFC107']

    fig, ax = plt.subplots(figsize=(8,8))
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title("Today's Macronutrient Breakdown")
    plt.axis('equal')

    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type='image/png')

# SignUp View
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def delete_consume(request, id):
    entry = get_object_or_404(Consume, id=id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('index')
    return HttpResponse("Invalid request", status=400)

@login_required
def edit_consume(request, id):
    entry = get_object_or_404(Consume, id=id, user=request.user)
    foods = Food.objects.all()

    if request.method == 'POST':
        new_food_name = request.POST.get('food_consumed')
        try:
            new_food = Food.objects.get(name=new_food_name)
            entry.food_consumed = new_food
            entry.save()
            return redirect('index')
        except Food.DoesNotExist:
            return HttpResponse("Invalid food selected", status=400)

    return render(request, 'myapp/edit.html', {
        'entry': entry,
        'foods': foods
    })



@login_required
def add_custom_food(request):
    if request.method == 'POST':
        name = request.POST['name'].strip()
        carbs = float(request.POST['carbs'])
        protein = float(request.POST['protein'])
        fats = float(request.POST['fats'])
        calories = int(request.POST['calories'])

        # Optional: check if food with this name already exists
        if not Food.objects.filter(name__iexact=name).exists():
            Food.objects.create(
                name=name,
                carbs=carbs,
                protein=protein,
                fats=fats,
                calories=calories
            )
    return redirect('index')
