"""
This module creates value within a system. A rule assigns a value to an object
type and the distribution of that value. A hook is an instantiation of such a
rule by picking a specific object in the system. Other objects that reference
this object trigger the hook and create the value for the receiving end of the
rule.
"""

from .models import Rule, Hook, Trigger
from .signals import fee_signal, hook_signal
from .shortcuts import listen, rule, rule_curry
