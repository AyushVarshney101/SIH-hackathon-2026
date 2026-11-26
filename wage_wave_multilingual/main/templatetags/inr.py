from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter(name='inr')
def inr(value):
	"""Format a number with Indian digit grouping: last 3 digits, then
	groups of 2 (e.g. 1840000 -> 18,40,000; 3200000 -> 32,00,000).

	Unlike floatformat/intcomma (Western thousands grouping: 1,840,000),
	this matches how amounts are actually written and read in India.
	"""
	try:
		number = int(Decimal(value).to_integral_value())
	except (InvalidOperation, TypeError, ValueError):
		return value

	negative = number < 0
	digits = str(abs(number))

	if len(digits) <= 3:
		grouped = digits
	else:
		last_three = digits[-3:]
		remaining = digits[:-3]
		parts = []
		while len(remaining) > 2:
			parts.insert(0, remaining[-2:])
			remaining = remaining[:-2]
		if remaining:
			parts.insert(0, remaining)
		grouped = ','.join(parts) + ',' + last_three

	return ('-' if negative else '') + grouped
