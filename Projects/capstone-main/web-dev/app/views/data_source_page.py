from django.views.generic import TemplateView


class DataSourceView(TemplateView):
    template_name = "app/views/data_sources_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta_title"] = "RIPE Explore"
        context["meta_description"] = (
            "Understand the different indicators used to visualize and analyze data."
        )
        return context
