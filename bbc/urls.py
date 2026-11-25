from django.urls import path
from .views import *
urlpatterns = [
    path("", articles, name = "home"),
    path("profile/", profile, name="profile"),
    path("registration/", registration, name = "registration"),
    path("verify/<int:id>/", verify_email, name = "verify_email"),
    path("resend/<int:id>/", resend_code, name = "resend_code"),
    path("login/", login_user, name = "login"),
    path("logout/", logout_user, name = "logout"),
    path("articles/", articles, name = "articles"),
    path("article/<int:id>/", article_detail, name = "article_detail"),
    path("comment/<int:id>/", write_comment, name = "write_comment"),
    path("uncomment/<int:id>/", delete_comment, name = "delete_comment"),
    path("create/", create_article, name = "create_article"),
    path("my_articles/", my_articles, name = "my_articles"),
    path("edit/<int:id>/", edit_own_article, name = "edit_own_article"),
    path("submit/<int:id>/", submit_own_article, name = "submit_own_article"),
    path("delete/<int:id>/", delete_own_article, name = "delete_own_article"),
    
    path("pending/", pending_list, name = "pending_list"),
    path("review/<int:id>/", review_article, name = "review_article"),
    path("approve/<int:id>/", approve_article, name = "approve_article"),
    path("reject/<int:id>/", reject_article, name = "reject_article"),
    path("remove/<int:id>/", remove_article, name = "remove_article"),
]