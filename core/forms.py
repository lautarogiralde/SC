from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Usuario


class Verificacion2FAForm(forms.Form):
    codigo_2fa = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': '123456',
                'autofocus': True,
                'class': 'form-control',
                'autocomplete': 'off',
            }
        ),
        label="Codigo de verificación",
        error_messages={
            'required': 'Ingrese el código de verificación.',
            'min_length': 'El código debe tener 6 dígitos.',
        },
    )

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        codigo_ingresado = cleaned_data.get('codigo_2fa')

        if not self.session:
            raise forms.ValidationError('Sesión no encontrada.')

        codigo_esperado = self.session.get('otp_code')
        otp_created_at = self.session.get('otp_created_at')

        if (
            not otp_created_at
            or (timezone.now().timestamp() - float(otp_created_at)) > 300
        ):
            raise forms.ValidationError('EXPIRED')

        if str(codigo_ingresado).strip() != str(codigo_esperado).strip():
            self.add_error(
                'codigo_2fa', 'El código ingresado es incorrecto. Vuelva a intentarlo.'
            )

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'El usuario o la contraseña ingresados son incorrectos. Inténtalo de nuevo.',
        'inactive': 'Esta cuenta se encuentra deshabilitada.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Usuario'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Contraseña'}
        )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            try:
                user = Usuario.objects.get(username=username)

                if not user.is_active:
                    raise forms.ValidationError(
                        self.error_messages['inactive'], code='inactive'
                    )
            except Usuario.DoesNotExist:
                pass

        return super().clean()
