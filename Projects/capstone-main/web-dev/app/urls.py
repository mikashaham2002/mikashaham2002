from django.urls import path
from . import views
from .views import (
    CountryListView,
    HomepageView,
    CountryProfileView,
    CompareCountryView,
    DataSourceView,
    DigitalInitiativesView,
)

urlpatterns = [
    path("", HomepageView.as_view(), name="home"),
    path("countries/", CountryListView.as_view(), name="country_reports"),
    path(
        "countries/<slug:country_slug>/",
        CountryProfileView.as_view(),
        name="profile",
    ),
    path("compare-country/", CompareCountryView.as_view(), name="compare-country"),
    path("search/", views.search_view, name="search_view"),
    path("income-classification/", views.income_filter, name="income-classification"),
    path("data-indicators/", DataSourceView.as_view(), name="data-indicators"),
    path(
        "digital-initiatives/",
        DigitalInitiativesView.as_view(),
        name="digital-initiatives",
    ),
]
