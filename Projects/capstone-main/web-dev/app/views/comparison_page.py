from django.views.generic import TemplateView
from django.conf import settings
import os
import pandas as pd
import json
from app.utils.generate_graphs import (
    generate_economic_graphs,
    generate_internet_graphs_compare,
)


class CompareCountryView(TemplateView):
    template_name = "app/views/comparison_page.html"

    def get(self, request, *args, **kwargs):
        # Get context data
        context = super().get_context_data(**kwargs)

        # Load country metadata from Excel file
        main_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "main-content.xlsx"
        )
        df_regions = pd.read_excel(main_file_path)
        df_regions["Prefix"] = df_regions["Prefix"].str.lower()  # Make Prefix lowercase
        country_reports = json.loads(df_regions.to_json(orient="records"))

        # Get selected countries from the request
        selected_countries_names = request.GET.getlist("country")

        # Filter list of countries based on the selected countries
        selected_countries_data = [
            country
            for country in country_reports
            if country["Name"] in selected_countries_names
        ]

        # Load graph data
        data_file_path = os.path.join(
            settings.BASE_DIR, "app", "data", "graph_data.json"
        )
        with open(data_file_path, "r") as file:
            graph_data = json.load(file)

        # Filter country data based on selected countries
        data = [
            entry
            for entry in graph_data
            if entry.get("Country Name") in selected_countries_names
        ]

        econ_graphs = []
        internet_graphs = []

        # Generate graphs for the selected country
        for country in selected_countries_names:
            # Filter the data for the current country
            country_data = [
                entry for entry in data if entry.get("Country Name") == country
            ]

            econ_graphs.append(
                (country, generate_economic_graphs(country_data, country))
            )

            internet_graphs.append(
                (country, generate_internet_graphs_compare(country_data, country))
            )

        # Add context for the template
        context["selected_countries_data"] = selected_countries_data
        context["selected_countries_names"] = selected_countries_names
        context["country_reports"] = country_reports
        context["econ_graphs"] = econ_graphs
        context["internet_graphs"] = internet_graphs
        context["meta_title"] = "Compare Countries"
        context["meta_description"] = (
            "Compare and analyze the differences between the selected countries"
        )

        # Return the response with context data
        return self.render_to_response(context)
