from django import forms

from timezones.utils import time_at


class LocationTimezoneAwareDateTimeField(forms.DateTimeField):
    pass


class LocationTimezoneAwareForm(forms.Form):
    def clean(self):
        first_pass = super(LocationTimezoneAwareForm, self).clean()

        for fieldname in self.fields.keys():
            field = self.fields[fieldname]
            if isinstance(field, LocationTimezoneAwareDateTimeField):
                if hasattr(self, 'location'):  # a location has been assigned to the form
                    try:
                        first_pass[fieldname] = time_at(first_pass[fieldname], self.location)
                    except KeyError:
                        pass

        return first_pass


class LocationTimezoneAwareModelForm(forms.ModelForm):
    def clean(self):
        first_pass = super(LocationTimezoneAwareModelForm, self).clean()

        for fieldname in self.fields.keys():
            field = self.fields[fieldname]
            if isinstance(field, LocationTimezoneAwareDateTimeField):
                if hasattr(self, 'location'):  # a location has been assigned to the form
                    try:
                        first_pass[fieldname] = time_at(first_pass[fieldname], self.location)
                    except KeyError:
                        pass

        return first_pass
