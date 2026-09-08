from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='اسم المستخدم',
        help_text='أدخل اسم مستخدم عربي أو إنجليزي بدون مسافات',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'اسم المستخدم'}),
        error_messages={
            'required': 'هذا الحقل مطلوب.',
            'invalid': 'أدخل اسم مستخدم صالحاً.',
        },
    )
    email = forms.EmailField(
        label='البريد الإلكتروني',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'البريد الإلكتروني'}),
        error_messages={'required': 'هذا الحقل مطلوب.', 'invalid': 'ادخل بريداً إلكترونياً صحيحاً.'},
    )
    phone_number = forms.CharField(
        label='رقم الهاتف',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'رقم الجوال'}),
    )
    password1 = forms.CharField(
        label='كلمة المرور',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'كلمة المرور'}),
        help_text='يجب أن تكون 8 أحرف على الأقل ولا تكون شائعة.',
        error_messages={'required': 'هذا الحقل مطلوب.'},
    )
    password2 = forms.CharField(
        label='تأكيد كلمة المرور',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'أعد كتابة كلمة المرور'}),
        help_text='أعد كتابة كلمة المرور نفسها',
        error_messages={'required': 'هذا الحقل مطلوب.'},
    )

    error_messages = {
        'password_mismatch': 'كلمتا المرور غير متطابقتين.',
    }

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={'placeholder': 'اسم المستخدم'}),
        error_messages={'required': 'هذا الحقل مطلوب.'},
    )
    password = forms.CharField(
        label='كلمة المرور',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'كلمة المرور'}),
        error_messages={'required': 'هذا الحقل مطلوب.'},
    )

    error_messages = {
        'invalid_login': 'اسم المستخدم أو كلمة المرور غير صحيحين.',
        'inactive': 'هذا الحساب غير مفعل.',
    }
