from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'pub_date', 'category',
                  'location', 'is_published')
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5}),
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'is_published': forms.CheckboxInput(),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст поста',
            'image': 'Изображение',
            'category': 'Категория',
            'location': 'Местоположение',
            'pub_date': 'Дата и время публикации',
            'is_published': 'Опубликовано',
        }
        help_texts = {
            'is_published': 'Снимите галочку, чтобы скрыть публикацию.',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Введите ваш комментарий...'}),
        }
        labels = {
            'text': 'Текст комментария'
        }