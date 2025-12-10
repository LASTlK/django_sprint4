from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('auth/logout/',
         auth_views.LogoutView.as_view(http_method_names=['get', 'post']),
         name='logout'),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('', include('blog.urls')),
    path('posts/', include('blog.urls')),
    path('category/', include('blog.urls')),
]


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.internal_server_error'
