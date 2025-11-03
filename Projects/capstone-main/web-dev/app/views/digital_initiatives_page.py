import pandas as pd
import json
import os
from django.views.generic import TemplateView
from django.conf import settings


class DigitalInitiativesView(TemplateView):
    template_name = "app/views/digital_initiatives_page.html"

    def get_context_data(self, **kwargs):
        # Get data from excel file
        main_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "digital-initiatives.xlsx"
        )
        df = pd.read_excel(main_file_path)
        digital_initiatives = json.loads(df.to_json(orient="records"))

        # Get country initials and sort them (needed for letter nav)
        country_initials = sorted(
            set(country["Name"][0].upper() for country in digital_initiatives)
        )

        context = super().get_context_data(**kwargs)
        # Pass context to the template
        context["meta_title"] = "RIPE Explore"
        context["meta_description"] = (
            "Explore international digital initatives applied to support the development of the internet infrastructure in an economic context."
        )
        context["digital_initiatives"] = digital_initiatives
        context["country_initials"] = country_initials
        return context
