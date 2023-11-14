from django.contrib import admin
from .models import AttemptedAnswer, Post, Reply, Subject, User, File, Quiz, Question, Attempt, Answer, Grade

#these models are displayed and can be manipulated
#in the admin panel
admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(User)
admin.site.register(File)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Attempt)
admin.site.register(AttemptedAnswer)
admin.site.register(Subject)
admin.site.register(Grade)