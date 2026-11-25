from django.db.models.signals import *
from django.dispatch import receiver
from .models import*
from django.contrib.auth.models import User



@receiver(post_save, sender=Articles)
def after_article_save(sender, instance, created, **kwargs):

    if created:
        print(f"{instance.author.username} создал артикль {instance.title}")
    else:
        print("не создано")


@receiver(post_save, sender=Comment)
def after_creating_comment(sender, instance, created, **kwargs):
    if created:
        print(f"{instance.author.username} создал комментарию под статью под номером {instance.article.id}")


@receiver(post_delete, sender=Articles)
def rejected_article(sender, instance, **kwargs):
    if instance.status in ['draft', 'rejected']:
        print(f"{instance.author.username} удалил свой артикль")
    else:
        print(f"Артикль под номером {instance.id} был удалён редактором")