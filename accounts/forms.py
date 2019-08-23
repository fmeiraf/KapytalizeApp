from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):

    class Meta:
        fields = ('first_name', 'username', 'email', 'password1', 'password2' )
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de usuario (utilizado para fazer login)'
        self.fields['email'].label = 'Email'
        self.fields['first_name'].label = 'Seu Nome'
