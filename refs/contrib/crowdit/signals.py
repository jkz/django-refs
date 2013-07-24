from django.dispatch import Signal

fee_signal = Signal(providing_args=['src', 'amount', 'currency'])
hook_signal = Signal(providing_args=['hook'])
