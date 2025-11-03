import plotly.graph_objs as go
import plotly.offline as pyo
from django.core.cache import cache

# Titles for all graphs and visualizations based on indicators
title_mapping = {
    "GNI per Capita": "GNI per Capita",
    "Foreign Investment": "Foreign Direct Investment",
    "Labor Force participation rate": "Labor Force Participation",
    "Unemployment Rate": "Unemployment Rate",
    "speed (mgps)": "Average Internet Speed",
    "bandwidth (kbit/s)": "Bandwidth Capacity",
    "asns_ris": "Number of ASNs",
    "v4_prefixes_ris": "IPv4 Prefix Count",
    "v6_prefixes_ris": "IPv6 Prefix Count",
    "Internet Penetration Rate": "Internet Penetration Rate",
}


# Set up caching keys
def generate_cache_key(identifier: str, country: str):
    # Create unique key based on country
    return f"{identifier}_{country}".replace(" ", "_").replace(":", "_")


def generate_economic_graphs(country_data, country_name):
    """
    Generates interactive economic graphs for the given country and indicators.

    Args:
        country_name (str): The name of the country
        country_data (list): All the economic and internet data for the given country

    Returns:
        dict: A dictionary containing the graphs for each economic indicator of the given country.
    """

    # Map economic indicators
    indicators = [
        "GNI per Capita",
        "Foreign Investment",
        "Labor Force participation rate",
        "Unemployment Rate",
    ]
    economy_graphs = {}
    for indicator in indicators:
        cache_key = generate_cache_key(f"economic_graph_{indicator}", country_name)
        cached_data = cache.get(cache_key)
        if cached_data:
            economy_graphs[indicator] = cached_data
        else:
            # Check if data for the indicator exists in the country data
            indicator_data = [
                entry
                for entry in country_data
                if entry["Country Name"] == country_name
                and indicator in entry
                and entry[indicator] is not None
            ]
            if indicator_data:
                # Generate the graph data for the indicator
                economy_graphs[indicator] = generate_economy_graph_data(
                    indicator, country_data, indicator_data
                )
                cache.set(cache_key, economy_graphs[indicator], timeout=None)
            else:
                economy_graphs[indicator] = {
                    "title": title_mapping.get(indicator, indicator),
                    "summary": "No Data Available",
                }
    return economy_graphs


# Generate internet infrastructure graphs
def generate_internet_graphs(country_data, country_name):
    """
    Generates interactive internet infrastructure graphs for the given country and indicators.

    Args:
        country_name (str): The name of the country
        country_data (list): All the economic and internet data for the given country

    Returns:
        dict: A dictionary containing the graphs for each internet indicator of the given country.
    """
    indicators = [
        "Internet Penetration Rate",
        "speed (mgps)",
        "bandwidth (kbit/s)",
        "asns_ris",
        "v4_prefixes_ris",
        "v6_prefixes_ris",
    ]

    internet_graphs = {}
    for indicator in indicators:
        cache_key = generate_cache_key(f"internet_graph_{indicator}", country_name)
        cached_data = cache.get(cache_key)

        if cached_data:
            # Use cached data
            internet_graphs[indicator] = cached_data
        else:
            # Get indicator data
            indicator_data = [
                entry
                for entry in country_data
                if entry["Country Name"] == country_name
                and indicator in entry
                and entry[indicator] is not None
            ]
            # If there is indicator data, generate the graph data
            if indicator_data:
                graph_data = generate_internet_graph_data(indicator, indicator_data)
                internet_graphs[indicator] = graph_data
                cache.set(cache_key, graph_data, timeout=None)  # Cache graph data
            else:
                internet_graphs[indicator] = {
                    "title": title_mapping.get(indicator, indicator),
                    "summary": "No Data Available",
                }

    return internet_graphs


def generate_economy_graph_data(indicator, country_data, indicator_data):
    """
    Extracts and plots the necessary economic data for the given country and indicators.

    Args:
        indicator (str): The name of the indicator
        country_data (list): All the economic and internet data for the given country

    Returns:
        dict: A dictionary containing the title and summary of key data.
    """

    # Format titles based on indicator names
    title = title_mapping.get(indicator, indicator)

    # Find earliest and latest data for the indicator
    earliest_data = None
    latest_data = None

    # Iterate through the data to get earliest and latest values
    for entry in country_data:
        if indicator in entry and entry[indicator] is not None:
            if earliest_data is None or entry["Year"] < earliest_data["Year"]:
                earliest_data = entry
            if latest_data is None or entry["Year"] > latest_data["Year"]:
                latest_data = entry

    if latest_data:
        latest_year = latest_data["Year"]
        latest_value = latest_data[indicator]

        if earliest_data:
            earliest_year = earliest_data["Year"]
            earliest_value = earliest_data[indicator]

            if earliest_value and earliest_value != 0:
                if indicator in ["Labor Force participation rate", "Unemployment Rate"]:
                    percentage_change = latest_value - earliest_value
                    arrow_icon = (
                        "<span class='icon icon-small icon-arrow-up'></span>"
                        if latest_value > earliest_value
                        else "<span class='icon icon-small icon-arrow-down'></span>"
                    )
                    change_text = f"{'increased' if latest_value > earliest_value else 'decreased'} by <span class='text-xl font-bold text-ncc-bright'>{abs(percentage_change):.2f}%</span> {arrow_icon}"
                elif indicator in ["GNI per Capita", "Foreign Investment"]:
                    times_increase = latest_value / earliest_value
                    arrow_icon = (
                        "<span class='icon icon-small icon-arrow-up'></span>"
                        if latest_value > earliest_value
                        else "<span class='icon icon-small icon-arrow-down'></span>"
                    )
                    change_text = f"{'increased' if latest_value > earliest_value else 'decreased'} by <span class='text-xl font-bold text-ncc-bright'>{abs(times_increase):.2f}×</span> {arrow_icon}"
            else:
                change_text = "N/A"
        else:
            earliest_year = None
            earliest_value = None
            change_text = "N/A"

        # Format values
        if indicator == "GNI per Capita" or indicator == "Foreign Investment":
            formatted_value = f"${latest_value:,.2f}"
        elif indicator in ["Labor Force participation rate", "Unemployment Rate"]:
            formatted_value = f"{latest_value:,.2f}%"
        else:
            formatted_value = str(latest_value)

        summary = f"""
            <div class='summary-block'>
                <p class='summary-text text-left'>
                    was <br><span class='text-xl font-bold text-ncc-bright'>{formatted_value}</span><br>
                    in <span class='text-lg font-semibold'>{latest_year},</span><br>
        """

        if earliest_year and earliest_value:
            summary += f"it {change_text} <br> since <span class='text-m font-semibold'>{earliest_year}</span></div>"

    else:
        summary = "No Data Available"

    graph_data = {
        "title": title,
        "summary": summary,
    }

    return graph_data


def generate_internet_graphs_compare(country_data, country_name):
    """
    Generates interactive internet infrastructure graphs for the given country and indicators.
    This function is used specifically for the compare page, using only 2 indicators.

    Args:
        country_name (str): The name of the country
        country_data (list): All the economic and internet data for the given country

    Returns:
        dict: A dictionary containing the graphs for each internet indicator of the given country.
    """
    # Select indicators for compare page
    indicators = [
        "Internet Penetration Rate",
        "speed (mgps)",
    ]

    internet_graphs = {}
    # Iterate through indicators, return cached content or generate economic graph for the given country
    for indicator in indicators:
        cache_key = generate_cache_key(f"internet_graph_{indicator}", country_name)
        cached_data = cache.get(cache_key)
        if cached_data:
            internet_graphs[indicator] = cached_data
        else:
            # Check if data for the indicator exists in the country data
            indicator_data = [
                entry
                for entry in country_data
                if entry["Country Name"] == country_name
                and indicator in entry
                and entry[indicator] is not None
            ]
            if indicator_data:
                # Generate the graph data for the indicator

                internet_graphs[indicator] = generate_internet_graph_data(
                    indicator, indicator_data
                )
                cache.set(cache_key, internet_graphs[indicator], timeout=None)
            else:
                internet_graphs[indicator] = {
                    "title": title_mapping.get(indicator, indicator),
                    "summary": "No Data Available",
                }

    return internet_graphs


def generate_internet_graph_data(indicator, indicator_data):
    """
    Extracts and plots the necessary internet data for the given country and indicators.
    Separates graph models based on indicators, internet penetration is a bar chart while
    other graphs are time series charts.

    Args:
        indicator (str): The name of the indicator
        indicator_data (list): All the data for the given indicator per year and country.

    Returns:
        dict: A dictionary containing the title and summary of key data.
    """

    # Format titles based on indicator names
    title = title_mapping.get(indicator, indicator)

    # For internet penetration, use different graph model since it is a bar chart
    if indicator == "Internet Penetration Rate":
        return generate_internet_penetration_rate_graph(indicator, indicator_data)

    # Get each year and corespondening value per indicator
    years = [entry["Year"] for entry in indicator_data]
    values = [entry[indicator] for entry in indicator_data]

    # Create plotly charts
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=years,
            y=values,
            mode="lines+markers",
            name=indicator,
            line=dict(color="#3a61e0"),
            hovertemplate="<b>Year:</b> %{x}<br><b>Value:</b> %{y}<extra></extra>",
        )
    )

    # Remove scrolling
    config = {
        "displayModeBar": False,
        "scrollZoom": False,
        "showLink": False,
        "displaylogo": False,
    }
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(
            showgrid=False,
            showticklabels=True,
            zeroline=False,
            tickmode="linear",
            dtick=2,
        ),
        yaxis=dict(showgrid=True, showticklabels=True, zeroline=False),
        template="plotly_white",
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
        dragmode=False,
    )

    plot_div = pyo.plot(fig, output_type="div", include_plotlyjs=False, config=config)

    # Extract latest data for plot summary
    latest_data = next(
        (
            entry
            for entry in reversed(indicator_data)
            if indicator in entry and entry[indicator] is not None
        ),
        None,
    )
    if latest_data:
        latest_year = latest_data["Year"]
        latest_value = latest_data[indicator]
        formatted_value = format_indicator_value(indicator, latest_value)
        summary = f"was <span class='text-xl font-bold text-ncc-bright'>{formatted_value}</span><br> in <span class='text-lg font-semibold'>{latest_year}</span><br>"
    else:
        summary = "No Data Available"

    return {"title": title, "plot_div": plot_div, "summary": summary}


# Extract and format data for internet penetration
def generate_internet_penetration_rate_graph(indicator, indicator_data):
    """
    Extracts and plots the necessary internet data for the given country and indicator values.
    Creates the bar chart plot.

    Args:
        indicator (str): The name of the indicator
        indicator_data (list): All the data for the given indicator per year and country.

    Returns:
        dict: A dictionary containing the title and summary of key data.
    """
    # Format titles based on indicator names
    title = title_mapping.get(indicator, indicator)

    data = [entry for entry in indicator_data if entry.get(indicator) is not None]
    # Return if no data found
    if not data:
        return {"title": title, "summary": "No Data Available"}

    # Get the earlier and latest data: year and rate
    earliest_data = data[0]
    latest_data = data[-1]

    latest_value = latest_data[indicator]
    latest_year = latest_data["Year"]
    earliest_value = earliest_data[indicator]
    earliest_year = earliest_data["Year"]

    # Set color for bars
    latest_bar_color = get_color_for_value(latest_value)
    earliest_bar_color = get_color_for_value(earliest_value)

    # Generate the bar chart
    bar_html = generate_bar_html(
        latest_value,
        latest_year,
        latest_bar_color,
        earliest_value,
        earliest_year,
        earliest_bar_color,
    )
    summary = f"<div class='summary-block'>{bar_html}</div>"

    return {"title": title, "bar_html": bar_html, "summary": summary}


# Logic for bar chart colors based on values
def get_color_for_value(value):
    """
    Assigns color to bar chart based on value. Green for high values over 70,
    Yellow for values between 40-70 and Red for everything below.

    Args:
        value (int): The internet penetration rate value.

    Returns:
        Hex code for color
    """

    if value >= 70:
        return "#28a745"  # Green
    elif value >= 40:
        return "#ffc107"  # Yellow
    return "#a40000"  # Red


# Generate html for bar chart
def generate_bar_html(
    latest_value,
    latest_year,
    latest_bar_color,
    earliest_value,
    earliest_year,
    earliest_bar_color,
):
    """
    Generates the bar chart html for internet penetration rate.

    Args:
        latest/earliest value (int): The internet penetration rate values.
        latest/earliest year (int): Earliest and latest year for when data was found (mostly 2015-2023).
        latest/earlier bar color (hex code): Color for bar chart (green, yellow, red)

    Returns:
        HTML for bar chart
    """

    return f"""

            <p class="text-left font-semibold text-lg">
                was <br>
                <span class="text-3xl font-bold text-ncc-bright">{latest_value:.2f}%</span><br>
                in <span class="text-lg font-semibold">{latest_year}</span>
            </p>
            <div class="w-full bg-gray-300 rounded-xl overflow-hidden mb-6">
                <div class="h-5" style="width: {latest_value}%; background: {latest_bar_color};"></div>
            </div>

            <p class="text-left font-semibold text-lg">
                compared to<br>
                <span class="text-2xl font-bold text-ncc-bright">{earliest_value:.2f}%</span><br>
                in <span class="text-lg font-semibold">{earliest_year}</span>
            </p>
            <div class="w-full bg-gray-300 rounded-xl overflow-hidden">
                <div class="h-5" style="width: {earliest_value}%; background: {earliest_bar_color};"></div>
            </div>

    """


def format_indicator_value(indicator, value):
    """
    Formats indicator values to make them readable.

    Args:
        indicator (str): Name of the indicator
        value: Indicator value

    Returns:
        Formatted indicator value
    """

    if indicator == "speed (mgps)":
        return f"{value:,.1f} MBit/s"
    if indicator == "bandwidth (kbit/s)":
        return f"{value:,.1f} Kbit/s"
    if indicator in ["asns_ris", "v4_prefixes_ris", "v6_prefixes_ris"]:
        return f"{round(value):,.0f}"
    return str(value)
