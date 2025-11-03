import pandas as pd
import json
import os
from django.views.generic import TemplateView
from django.conf import settings


class HomepageView(TemplateView):
    template_name = "app/views/homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get data from excel file
        main_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "main-content.xlsx"
        )
        df = pd.read_excel(main_file_path)

        # Lower country codes
        df["Prefix"] = df["Prefix"].str.lower()
        country_reports = json.loads(df.to_json(orient="records"))

        # Dictionary mapping country names to colors
        color_mapping = {
            country["Name"]: country["Color_Overall_2023"]
            for country in country_reports
            if country.get("Color_Overall_2023")
        }

        # Tooltip mapping
        tooltip_mapping = {
            country["Name"]: {
                "Overall": country.get("Overall_Index_2023", "Unknown"),
                "GNI": country.get("GNI_Economic_Index_2023", "Unknown"),
                "Internet": country.get("Internet_Index_2023", "Unknwon"),
            }
            for country in country_reports
        }

        # Convert unkown values for index table
        for country in country_reports:
            if country.get("Overall_Index_2023") == "Unknown":
                country["Overall_Index_2023"] = "&ndash;"
            if country.get("Rank") == "Unknown":
                country["Rank"] = "&ndash;"
            if country.get("Score_Change") == "Unknown":
                country["Score_Change"] = "&ndash;"

        context["tooltip_mapping"] = json.dumps(tooltip_mapping, ensure_ascii=False)
        context["color_mapping"] = json.dumps(color_mapping, ensure_ascii=False)
        context["country_reports"] = country_reports
        context["meta_title"] = "RIPE Explore"
        context["meta_description"] = (
            "Explore the connections between internet infrastructure, connectivity and economic growth. Discover real-world examples highlighting the vital role of internet infrastructure in shaping economic progress."
        )
        return context
