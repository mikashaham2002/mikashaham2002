import pandas as pd
import json
import os
from django.views.generic import TemplateView
from django.conf import settings
from app.utils.generate_graphs import generate_economic_graphs, generate_internet_graphs


class CountryProfileView(TemplateView):
    template_name = "app/views/country_profile_page.html"

    def get_slug(self, **kwargs):
        return kwargs.get("country_slug")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Load all country information from Excel file
        main_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "main-content.xlsx"
        )
        df_regions = pd.read_excel(main_file_path)
        df_regions["Prefix"] = df_regions["Prefix"].str.lower()
        country_reports = json.loads(df_regions.to_json(orient="records"))

        # Find country based on the slug
        country_slug = self.get_slug(**kwargs)
        for value in country_reports:
            if value["Slug"] == country_slug:
                country = value
        country_name = country["Name"]

        # Load graph data
        data_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "graph_data.json"
        )
        with open(data_file_path, "r") as file:
            graph_data = json.load(file)

        # Extract country data based on the name
        country_data = [
            entry
            for entry in graph_data
            if entry.get("Country Name") == country["Name"]
        ]

        # Generate graphs for economic and internet indicators
        econ_graphs = generate_economic_graphs(country_data, country_name)
        internet_graphs = generate_internet_graphs(country_data, country_name)

        # Add context for the template
        context["meta_title"] = f"{country['Name']}"
        context["meta_description"] = (
            "Analyze the economic and internet indicators of the selected country."
        )
        context["country_reports"] = country_reports
        context["country"] = country
        context["econ_graphs"] = econ_graphs
        context["internet_graphs"] = internet_graphs

        return context
