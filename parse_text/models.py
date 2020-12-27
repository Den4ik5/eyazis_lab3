from django.db import models


class Document(models.Model):
    name = models.CharField(max_length=1000, null=True)
    text = models.TextField()
    language = models.CharField(max_length=20, null=False)
    theme = models.CharField(max_length=60, null=False, default='')
    args = models.TextField()


class Note(models.Model):
    document_id = models.ForeignKey('Document', on_delete=models.CASCADE)
    text = models.TextField()
    text_for_algo = models.TextField()
    text_for_ml = models.TextField(default='')



