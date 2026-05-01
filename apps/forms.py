from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.fields import CharField


class RegisterUserModelForm(UserCreationForm):
    password1 = CharField(max_length=50)
    password2 = CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')



    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.pop('password2', None)
        if password1 != password2:
            raise ValidationError("Passwords don't match")
        return super().clean()

    def save(self, commit=True):
        user = super().save(False)
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user