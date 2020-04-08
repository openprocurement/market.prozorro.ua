from rest_framework.exceptions import ValidationError

class ValidateRequiredFieldsMixin:
    REQUIRED_FIELDS = ()

    def validate(self, data):
        try:
            data['id'] # passed id makes required fields optional
        except KeyError:
            possible_errors = self._check_required_fields(data)
            if possible_errors:
                error_dict = {}
                for error in possible_errors:
                    error_dict[error] = 'This field is required.'
                raise ValidationError(error_dict)
        return data

    def _check_required_fields(self, data):
        errors = []
        for field in self.REQUIRED_FIELDS:
            try:
                data[field]
            except KeyError:
                errors.append(field)
        return errors
