from django.contrib import admin
<<<<<<< Updated upstream
from .models import AttemptedAnswer, Post, Reply, User, File, Subject, Question, Attempt, Answer
=======
from .models import AttemptedAnswer, Post, Reply, Subject, User, File, Quiz, Question, Attempt, Answer
>>>>>>> Stashed changes

#these models are displayed and can be manipulated
#in the admin panel
admin.site.register(Post)
admin.site.register(Reply)
admin.site.register(User)
admin.site.register(File)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Attempt)
admin.site.register(AttemptedAnswer)
admin.site.register(Subject)