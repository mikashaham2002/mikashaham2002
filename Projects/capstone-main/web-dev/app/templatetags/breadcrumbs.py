from django import template

register = template.Library()


@register.inclusion_tag("app/templatetags/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    request = context["request"]
    path = request.path.strip("/")

    breadcrumbs = []
    if path:
        elements = path.split("/")
        url = "/"
        for element in elements:
            url += element + "/"
            breadcrumbs.append({"name": element.replace("_", " "), "url": url})

    return {"breadcrumbs": breadcrumbs}
