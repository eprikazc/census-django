from django import template
register = template.Library()

@register.filter(name='clean_stat_name')
def clean_stat_name(value):
    return value.split(" [")[0].upper()

@register.filter(name='add_commas')
def add_commas(value):
    value = str(value)
    res = ""
    for i in range(len(value), 0, -1):
        res = "%s%s" %(value[i-1], res)
        if len(res.replace(",", ""))%3 == 0:
            res = ",%s" %res
    return res.strip(",")

@register.assignment_tag(takes_context=True)
def get_context_value(context, key_name):
    data = []
    for elem in context[key_name]:
        data.append([elem[0], elem[1], int(elem[2])])
    return data
