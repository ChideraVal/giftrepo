from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import Gift, User
import random


class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        # self.fields["username"].widget.attrs['autocomplete'] = 'off'
        self.fields["username"].label = 'Email Address'


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.fields["username"].widget.attrs['autocomplete'] = 'off'
        self.fields["username"].widget.attrs['autofocus'] = 'on'
        # self.fields["email"].widget.attrs['autocomplete'] = 'off'
        self.fields["email"].label = 'Email Address'

    
    class Meta:
        model = User
        fields = ['username', 'email', 'gender']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'})
        }

        labels = {
            'email': 'Email Address'
        }

        error_messages = {
            'email': {
                'unique': "This email is already associated with another account."
            }
        }

        help_texts = {
            'email': "When you change your email address, the new address isn't set immediately, instead an email will be sent to the new address with a link to verify the new address. Click the link to finalize changes."
        }


class GiftForm(forms.ModelForm):
    class Meta:
        model = GiftTransaction
        fields = ['quantity', 'is_fastest_finger', 'is_visible', 'expire_rate', 'drop_rate']

        labels = {
            'is_fastest_finger': 'Fastest Finger (FF)',
            'is_visible': 'Show Gift',
            'early_claim_fee': 'Early Claim Fee',
            # 'claim_fee': 'Claim Fee',
            'expire_rate': 'Expire Rate',
            'drop_rate': 'Drop Rate'

        }

        # widgets = {
        #     'quantity': forms.NumberInput(attrs={'min': 1, 'max': 100}),
        # }

    def clean(self):
        cleaned_data = super().clean()
        quantity = self.cleaned_data.get('quantity')
        expire_rate = cleaned_data.get('expire_rate')
        drop_rate = cleaned_data.get('drop_rate')
        is_fastest_finger = cleaned_data.get('is_fastest_finger')
        early_claim_fee = cleaned_data.get('early_claim_fee')
        # claim_fee = cleaned_data.get('claim_fee')

        if quantity <= 0:
            raise forms.ValidationError('Quantity must be greater than 0.')
        
        # temporary condition to max expire rate to 24 hrs
        if expire_rate < 1 or expire_rate > 24:
            raise forms.ValidationError('Expire rate must be between 1 and 24.')
        
        # temporary condition to max drop rate to 23 hrs
        if drop_rate > 23:
            raise forms.ValidationError('Drop rate must be between 0 and 23.')
        
        if expire_rate <= drop_rate:
            raise forms.ValidationError('Expire rate must be greater than drop rate.')
        
        # if is_fastest_finger and drop_rate == 0:
        #     raise forms.ValidationError('FF gifts must have drop rates greater than 0.')
        
        if is_fastest_finger and drop_rate > 0:
            raise forms.ValidationError('Drop rates for FF gifts must be 0.')
        
        # temporary condition to disable wait time for normal gifts
        # if not is_fastest_finger and drop_rate > 0:
        #     raise forms.ValidationError('Drop rates for non FF gifts must be 0.')

        # if is_fastest_finger and early_claim_fee > 0:
        #     raise forms.ValidationError('FF gifts must not have early claim fee greater than 0.')  CHANGE LATER

        # previous validator to allow claim fee for only FF gifts
        # if not is_fastest_finger and claim_fee:
        #     raise forms.ValidationError('Only FF gifts can have FF entry fee.')
        
        # FIX ERROR MESSAGE TEXT
        # if drop_rate == 0 and early_claim_fee > 0:
        #     raise forms.ValidationError('Gifts with drop rate of 0 cannot have early claim fee greater than 0.') CHANGE LATER
        
        return cleaned_data
