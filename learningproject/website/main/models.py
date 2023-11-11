from django.db import models
from django.contrib.auth.models import User, AbstractUser
from mimetypes import guess_type

#custom user model
class User(AbstractUser):
    is_teacher = models.BooleanField('Is teacher', default=False)
    is_student = models.BooleanField('Is student', default=False)

#post model
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_of_replies = 0

    def __str__(self):
    
        return self.title + "\n" + self.description

#reply model
class Reply(models.Model):
    post = models.ForeignKey(Post, related_name="replies", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE) #different from the author of the post / reply_author
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author.username + "\n" + self.description

#file model    
class File(models.Model):
    file = models.FileField(upload_to="gen/")
    post = models.ForeignKey(Post, related_name="files", on_delete=models.CASCADE)

    #this function converts file types into a string
    #to determine appropriate file tags
    def gethtml(file):
        type_tuple = guess_type(file.file.url, strict=True)
        if (type_tuple[0]).__contains__("image"):
            return "image"
        elif (type_tuple[0]).__contains__("video"):
            return "video"
        elif (type_tuple[0]).__contains__("text"):
            return "text"
        elif (type_tuple[0]).__contains__("application"):
            return "application"
        elif (type_tuple[0]).__contains__("msword"):
            return "msword"
        elif (type_tuple[0]).__contains__("vnd.openxmlformats-officedocument.wordprocessingml.document"):
            return "document"
        
#subject model
class Subject(models.Model):
    title = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, null=True, on_delete=models.CASCADE)


#quiz model
class Quiz(models.Model):
    subject = models.ForeignKey(Subject, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    weight = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=0)
    max_attempts = models.IntegerField(default=3)

    def __str__(self):
        return self.title

#question model
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", null=True, on_delete=models.CASCADE)
    text = models.CharField('Question', max_length=255, blank=True)

    def __str__(self):
        return self.text

#answer model
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    text = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return str("Question: " + self.question.text + " Answer:" + self.text)

#attempt model
class Attempt(models.Model):
    student = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, null=True, related_name="attempts", on_delete=models.CASCADE)
    number = models.IntegerField(default=0)
    score = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=0)


#AttemptedAnswer model
class AttemptedAnswer(models.Model):
    answer = models.ForeignKey(Answer, null=True, on_delete=models.CASCADE)
    attempt = models.ForeignKey(Attempt, null=True, related_name="attempted_answers", on_delete=models.CASCADE)
