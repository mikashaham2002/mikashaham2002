import pandas as pd
import json
import os
from django.views.generic import TemplateView
from django.conf import settings


class CountryListView(TemplateView):
    template_name = "app/views/list_countries_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Read data from excel file
        main_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "main-content.xlsx"
        )
        df_regions = pd.read_excel(main_file_path)

        # Lower country codes
        df_regions["Prefix"] = df_regions["Prefix"].str.lower()
        country_reports = json.loads(df_regions.to_json(orient="records"))

        # Extract and sort country initials (for letter nav)
        country_initials = sorted(
            set(country["Name"][0].upper() for country in country_reports)
        )

        # Pass context to template
        context["meta_title"] = "Country Reports"
        context["meta_description"] = (
            "Discover the internet and economic dveelopment of each country within the NCC regions. "
        )
        context["country_reports"] = country_reports
        context["country_initials"] = country_initials
        return context
