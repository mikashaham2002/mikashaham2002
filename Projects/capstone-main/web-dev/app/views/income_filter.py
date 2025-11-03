from django.shortcuts import render
from django.conf import settings
import pandas as pd
import os
import json


def load_countries():
    main_file_path = os.path.join(settings.BASE_DIR, "app", "data", "main-content.xlsx")
    df = pd.read_excel(main_file_path)
    df["Prefix"] = df["Prefix"].str.lower()
    df["Income_Class"] = df["Income_Class"].astype(str).str.strip().str.lower()

    return json.loads(df.to_json(orient="records"))


def income_filter(request):
    country_reports = load_countries()

    income_mapping = {
        "high income country": "high income",
        "upper middle income country": "upper middle income",
        "lower middle income country": "lower middle income",
        "low income country": "low income",
    }

    income_class = request.GET.get("income_class")

    if income_class:
        income_class = income_class.strip().lower()
        income_class = income_mapping.get(income_class, income_class)

    filtered_countries = [
        country
        for country in country_reports
        if country.get("Income_Class", "").strip().lower() == income_class
    ]

    country_initials = sorted(
        set(country["Name"][0].upper() for country in filtered_countries)
    )
    meta_title = "Filter by Income"
    meta_description = "Explore countries based on their income level classification."

    return render(
        request,
        "app/views/income_filtered_page.html",
        {
            "filtered_countries": filtered_countries,
            "income_class": income_class,
            "country_initials": country_initials,
            "meta_title": meta_title,
            "meta_description": meta_description,
        },
    )
