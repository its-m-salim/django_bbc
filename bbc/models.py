from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Articles(models.Model):

    STATUSES = [
        ("draft","Черновик"),
        ("pending", "На проверке"),
        ("approved", "Одобрено"),
        ("rejected", "Отказано")
    ]

    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete= models.CASCADE, related_name="articles")
    category = models.ForeignKey(Category, on_delete= models.CASCADE, related_name="articles")
    status = models.CharField(max_length=10, choices=STATUSES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey(User, null = True, blank=True, on_delete=models.SET_NULL, related_name="approved_articles")

    class Meta:
        default_permissions = ()
        permissions = [
            ("write_articles", "Can write articlessss"),
            ("edit_own_article", "Can edit own article"),
            ("submit_article", "Can submit article"),
            ("review_article", "Can review pending articles"),
            ("publish_article", "Can publish article"),
            ("remove_article", "Can delete any article"),
            ("reject_article", "Can reject reviewed articles"),
            ("approve_article", "Can approve any reviewed articles")
        ]


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = [
            ("write_comment", "Can write comments"),
            ("remove comment", "Can delete any comments")
        ]


class EmailCode(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    code = models.CharField(max_length=6)