from django import template

register = template.Library()

@register.filter(name='is_attempted')
def is_attempted(answer, attempt):
    return attempt.attempted_answers.filter(answer=answer).exists()