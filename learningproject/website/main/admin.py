from django.contrib import admin
from .models import Post, Reply, Score, User, File, Subject, Question, Attempt

#these models are displayed and can be manipulated
#in the admin panel
admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(User)
admin.site.register(File)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Score)
admin.site.register(Attempt)