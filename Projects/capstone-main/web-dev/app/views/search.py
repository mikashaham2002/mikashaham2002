import json
import os
import pandas as pd
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404
import re


def generate_slug(name):
    return re.sub(r"\s+", "-", name.strip().lower())


# Function to load country data from Excel
def load_countries():
    main_file_path = os.path.join(settings.BASE_DIR, "app", "data", "main-content.xlsx")
    df = pd.read_excel(main_file_path)
    df["Prefix"] = df["Prefix"].str.lower()  # Lower country codes
    country_reports = json.loads(df.to_json(orient="records"))
    return country_reports


# Search view
def search_view(request):
    query = request.GET.get("query")
    country_reports = load_countries()

    # Normalize query to match country profile url
    normalized_query = generate_slug(query)
    country = next(
        (item for item in country_reports if item["Slug"] == normalized_query), None
    )

    if country:
        return redirect("profile", country_slug=country["Slug"])
    else:
        raise Http404("Country not found")
