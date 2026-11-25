from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.models import Group, User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count, Prefetch
from django.core.mail import send_mail
import random




def home_page(request):
    return render(request, 'home.html')




@login_required
def profile(request):
    user = request.user
    names = user.groups.values_list("name", flat=True)

    if "Editors" in names:

        role, role_label = "editor", "Редактор"
    
    elif "Journalists" in names:
    
        role, role_label = "journalist", "Журналист"
    else:
    
        role, role_label = "reader", "Читатель"

    created_count = Articles.objects.filter(author=user).count()

    published_count = 0
    
    if role == "editor":
        published_count = Articles.objects.filter(approved_by=user).count()

    return render(request, "profile.html", {
        "role": role,
        "role_label": role_label,
        "created_count": created_count,
        "published_count": published_count,
    })





def send_code(user):
    code = str(random.randint(100000, 999999))
    EmailCode.objects.update_or_create(
        user = user,
        defaults = {"code": code}
    )


    send_mail(
        "Код подтверждения",
        f"Ваш код подтверждения: {code}",
        None,
        [user.email]
    )



def registration(request):
    if request.method == "POST":
        data = request.POST

        if  User.objects.filter(username = data['username']).exists():
            return render(request, "registration.html", {"error": "Такой логин уже занят"})

        if User.objects.filter(email=data['email']).exists():
            return render(request, "registration.html", {"error": "Эта почта уже используется"})
        

        user = User.objects.create_user(
            username = data['username'],
            password = data['password'],
            email = data['email'],
            is_active = False
        )

        send_code(user)

        return redirect("verify_email", id = user.id)

    return render(request, "registration.html")



def verify_email(request, id):

    user = get_object_or_404(User, pk = id, is_active = False)

    if request.method == "POST":
        code = request.POST['code']
        record = EmailCode.objects.filter(user = user, code = code).first()

        if record is None:
            return render(request, "verify_email.html", {"user_id": user.id, "error": "Неверный код"})

        user.is_active = True
        user.save()
        record.delete()

        readers, _ = Group.objects.get_or_create(name = "Readers")
        user.groups.add(readers)

        login(request, user)
        return redirect("home")

    return render(request, "verify_email.html", {"user_id": user.id})



def login_user(request):
    if request.method == "POST":
        data = request.POST
        username = data["username"]
        password = data["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        inactive = User.objects.filter(username=username, is_active=False).first()

        if inactive is not None and inactive.check_password(password):
            send_code(inactive)
            return redirect("verify_email", id=inactive.id)

        return render(request, "login.html", {"error": "Неверный логин или пароль"})

    return render(request, "login.html")



def resend_code(request, id):
    user = get_object_or_404(User, pk = id, is_active = False)

    if request.method == "POST":
        send_code(user)

    return redirect("verify_email", id=user.id)




@login_required
def logout_user(request):
    logout(request)
    return redirect("login")





@login_required
@permission_required("bbc.write_articles", raise_exception=True)
def create_article(request):
    if request.method == "POST":
        data = request.POST

        Articles.objects.create(
            title = data['title'],
            content = data['content'],
            author = request.user,
            category = get_object_or_404(Category, pk = data['category'])
        )

        return redirect("my_articles")

    return render(request, "write_article.html", {"categories": Category.objects.all()})





@login_required
def my_articles(request):
    articles = Articles.objects.filter(author = request.user).select_related("category").order_by("created_at")

    return render(request, "my_articles.html", {"articles": articles})





@login_required
@permission_required("bbc.submit_article", raise_exception=True)
def submit_own_article(request, id):
    if request.method == "POST":
        article = get_object_or_404(Articles, pk = id, author = request.user, status__in = ["draft", "rejected"])
        article.status = "pending"
        article.save()

        return redirect("my_articles")




@login_required
@permission_required("bbc.edit_own_article", raise_exception=True)
def edit_own_article(request, id):
    article = get_object_or_404(Articles, pk = id, author = request.user, status__in = ["draft", "rejected"])
    if request.method == "POST":
        data = request.POST

        article.title = data['title']
        article.content = data['content']
        article.category = get_object_or_404(Category, pk = data['category'])
        article.status = "draft"
        article.save()

        return redirect("my_articles")

    return render(request, "edit_article.html", {"categories": Category.objects.all(), "article": article})



@login_required
def delete_own_article(request, id):
    article = get_object_or_404(Articles, pk = id, author = request.user, status__in = ["draft", "rejected"])

    if request.method == 'POST':
        article.delete()

        return redirect("my_articles")











@login_required
@permission_required("bbc.review_article", raise_exception=True)
def pending_list(request):
    articles = Articles.objects.filter(status = "pending").select_related("author", "category").order_by("created_at")

    return render(request, "pending_list.html", {"articles": articles})




@login_required
@permission_required("bbc.review_article", raise_exception=True)
def review_article(request, id):
    article = get_object_or_404(Articles.objects.select_related("author", "category"), pk = id, status = "pending")

    return render(request, "review_article.html", {"article": article})



@login_required
@permission_required("bbc.approve_article", raise_exception=True)
def approve_article(request, id ):
    article = get_object_or_404(Articles, pk = id, status = "pending")

    if request.method == "POST":
        article.status = "approved"
        article.approved_by = request.user
        article.save()
        return redirect("pending_list")




@login_required
@permission_required("bbc.remove_article", raise_exception=True)
def remove_article(request, id):
    article = get_object_or_404(Articles.objects.exclude(status = "draft"), pk = id)

    if request.method == "POST":
        article.delete()
        return redirect("articles")



@login_required
@permission_required("bbc.reject_article", raise_exception=True)
def reject_article(request, id):
    article = get_object_or_404(Articles, pk = id, status = "pending")

    if request.method == "POST":
        article.status = 'rejected'
        article.save()
        return redirect("pending_list")





def articles(request):
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")

    items = (
        Articles.objects
        .filter(status="approved")
        .select_related("author", "category")
        .annotate(comments_count=Count("comments"))
        .order_by("-created_at")
    )

    if q:
        items = items.filter(Q(title__icontains=q) | Q(content__icontains=q))

    selected = int(category) if category.isdigit() else None

    if selected:
        items = items.filter(category_id=selected)

    context = {
        "articles": items,
        "categories": Category.objects.all(),
        "q": q,
        "selected_category": selected,
    }

    return render(request, "articles.html", context)






def article_detail(request, id):

    article = get_object_or_404(
        Articles.objects.filter(status = "approved")
        .select_related("author", "category")
        .prefetch_related(
            Prefetch("comments", queryset=Comment.objects.select_related("author"))
        ),
        pk = id

    )

    return render(request, "article_detail.html", {"article": article})




@login_required
@permission_required("bbc.write_comment", raise_exception=True)
def write_comment(request, id):
    article = get_object_or_404(Articles, pk = id, status = "approved")
    if request.method == "POST":
        data = request.POST

        Comment.objects.create(
            author = request.user,
            text = data['text'],
            article = article
        )

        return redirect("article_detail", id = article.id)

    return render(request, 'write_comment.html', {"article": article})



@login_required
@permission_required("bbc.remove_comment", raise_exception=True)
def delete_comment(request, id):
    comment = get_object_or_404(Comment, pk =id)

    article_id  = comment.article_id


    if request.method == "POST":
        comment.delete()

    return redirect("article_detail", id = article_id)


