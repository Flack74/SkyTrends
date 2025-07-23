#!/usr/bin/env python3
# app.py - Airline Demand Analysis Web App
# Author: Flack74

import os
import json
import requests
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from airports import COMMON_AIRPORTS, search_airports, get_airport_by_code

# Set API key (use environment variable if available, otherwise use demo)
API_KEY = os.environ.get("API_KEY", "demo")  # Default to demo key if not provided

app = Flask(__name__)


@app.context_processor
def inject_context():
    """Add common variables to all template contexts."""
    from datetime import datetime

    return {
        "current_year": datetime.now().year,
        "get_airport_by_code": get_airport_by_code,
    }


def fetch_api_data(origin, destination, start_date, end_date):
    """
    Fetch flight data from Travelpayouts API.

    Args:
        origin (str): Origin IATA code
        destination (str): Destination IATA code (or "ANY")
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        list: List of flight dictionaries
    """
    # Use Travelpayouts API for flight prices
    base_url = "https://api.travelpayouts.com/v2/prices/latest"

    params = {
        "origin": origin,
        "period_type": "range",
        "beginning_of_period": start_date,
        "end_of_period": end_date,
        "limit": 100,
        "token": API_KEY,
    }

    # Add destination only if not "ANY"
    if destination and destination.upper() != "ANY":
        params["destination"] = destination

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return []


def scrape_backup(origin, destination, start_date, end_date):
    """
    Scrape flight data as backup when API fails or returns limited data.

    Args:
        origin (str): Origin IATA code
        destination (str): Destination IATA code (or "ANY")
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format

    Returns:
        list: List of flight dictionaries
    """
    # This is a fallback function that would normally scrape a website
    # For demo purposes, we'll return some sample data
    sample_data = []

    # Generate some sample data if API returned nothing
    if destination.upper() == "ANY":
        destinations = ["JFK", "LAX", "LHR", "CDG", "SYD"]
    else:
        destinations = [destination]

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1

    for dest in destinations:
        for i in range(days):
            current_date = start + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            price = 200 + (
                hash(f"{origin}{dest}{date_str}") % 300
            )  # Random but consistent price

            sample_data.append(
                {
                    "origin": origin,
                    "destination": dest,
                    "depart_date": date_str,
                    "return_date": (current_date + timedelta(days=7)).strftime(
                        "%Y-%m-%d"
                    ),
                    "price": price,
                    "airline": "DEMO",
                    "flight_number": f"DM{100 + i}",
                    "source": "scraper",
                }
            )

    return sample_data


def analyze(data):
    """
    Analyze flight data using Python data structures.

    Args:
        data (list): List of flight dictionaries

    Returns:
        dict: Dictionary containing analysis results
    """
    if not data:
        return {
            "top_routes": [],
            "price_trends": [],
            "summary": {
                "total_routes": 0,
                "avg_price": 0,
                "min_price": 0,
                "max_price": 0,
            },
        }

    # Count routes
    route_counter = Counter()
    for flight in data:
        route = (flight["origin"], flight["destination"])
        route_counter[route] += 1

    # Top routes by frequency
    top_routes = []
    for (origin, destination), count in route_counter.most_common(10):
        top_routes.append(
            {"origin": origin, "destination": destination, "count": count}
        )

    # Price trends over time
    date_prices = defaultdict(list)
    for flight in data:
        date = flight["depart_date"]
        date_prices[date].append(flight["price"])

    price_trends = []
    for date, prices in date_prices.items():
        avg_price = sum(prices) / len(prices) if prices else 0
        price_trends.append({"depart_date": date, "price": round(avg_price, 2)})

    # Sort price trends by date
    price_trends.sort(key=lambda x: x["depart_date"])

    # Summary statistics
    prices = [flight["price"] for flight in data]
    summary = {
        "total_routes": len(data),
        "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
        "min_price": min(prices) if prices else 0,
        "max_price": max(prices) if prices else 0,
    }

    return {"top_routes": top_routes, "price_trends": price_trends, "summary": summary}


@app.route("/")
def index():
    """Render the home page with the search form."""
    return render_template("index.html", airports=COMMON_AIRPORTS)


@app.route("/search_airport")
def search_airport():
    """Search for airports based on query."""
    query = request.args.get("q", "")
    if len(query) < 2:
        return jsonify([])

    results = search_airports(query)
    return jsonify(results)


def is_valid_search_input(origin, start_date, end_date):
    """Check if the search input is valid.

    Args:
        origin (str): Origin IATA code
        start_date (str): Start date
        end_date (str): End date

    Returns:
        bool: True if all required fields are provided, False otherwise
    """
    has_origin = bool(origin)
    has_start_date = bool(start_date)
    has_end_date = bool(end_date)

    return has_origin and has_start_date and has_end_date


@app.route("/results", methods=["POST"])
def results():
    """Process form data and display results."""
    origin_code = request.form.get("origin", "").upper()
    destination_code = request.form.get("destination", "").upper()
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    # Get airport details
    origin_airport = get_airport_by_code(origin_code) if origin_code else None
    destination_airport = (
        get_airport_by_code(destination_code)
        if destination_code and destination_code != "ANY"
        else None
    )

    # Use codes for API calls
    origin = origin_code
    destination = destination_code

    # Validate inputs
    if not is_valid_search_input(origin, start_date, end_date):
        return render_template(
            "index.html", error="All fields except destination are required"
        )

    # Fetch data from API
    try:
        api_data = fetch_api_data(origin, destination, start_date, end_date)

        # If API data is insufficient, supplement with scraped data
        if len(api_data) < 10:
            scraped_data = scrape_backup(origin, destination, start_date, end_date)
            combined_data = api_data + scraped_data
            data_source = "API and generated data"
        else:
            combined_data = api_data
            data_source = "API data"
    except Exception as e:
        # If API fails completely, use only scraped data
        print(f"Error fetching API data: {e}")
        scraped_data = scrape_backup(origin, destination, start_date, end_date)
        combined_data = scraped_data
        data_source = "Generated data (API unavailable)"

    # Analyze the data
    analysis_results = analyze(combined_data)

    # Pass data to template
    return render_template(
        "results.html",
        origin=origin,
        destination=destination if destination else "ANY",
        start_date=start_date,
        end_date=end_date,
        results=analysis_results,
        data_source=data_source,
    )


@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    """
    Process AI questions about travel and flight data using OpenRouter API with Qwen model.

    This endpoint accepts POST requests with a JSON body containing a 'question' field.
    It sends the question to the OpenRouter API using the Qwen model and returns the
    formatted response with proper HTML styling for display in the UI.

    Returns:
        JSON response with formatted HTML answer or error message
    """

    try:
        # Get question from request
        data = request.get_json()
        question = data.get("question", "")

        # Get AI API key from environment
        ai_key = os.environ.get("AI_KEY", "")
        if not ai_key:
            return (
                jsonify(
                    {
                        "response": "<p>AI API key not configured. Please add AI_KEY to your .env file.</p>"
                    }
                ),
                400,
            )

        # Prepare prompt with travel context
        prompt = f"""You are a travel and airline industry expert assistant. 
        Answer the following question about travel, flights, or airline industry trends.
        
        Question: {question}
        
        Provide a helpful, informative response based on your knowledge of the airline industry, 
        travel patterns, and flight pricing. Include specific insights when possible."""

        # Call OpenRouter API with Qwen model
        headers = {
            "Authorization": f"Bearer {ai_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "qwen/qwen3-235b-a22b-07-25:free",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a travel and airline industry expert assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500,
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        if response.status_code == 200:
            ai_response = response.json()
            answer = (
                ai_response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            # Simple formatting for clean, readable responses like ChatGPT/Perplexity

            # Step 1: Clean up the text and prepare for formatting
            answer = answer.strip()

            # Step 2: Convert markdown headings to HTML headings with proper styling
            for i in range(3, 0, -1):
                heading_marker = "#" * i
                answer = re.sub(
                    f"^{heading_marker}\s+(.+)$",
                    f"<h{i+2}>\\1</h{i+2}>",
                    answer,
                    flags=re.MULTILINE,
                )

            # Step 3: Convert markdown bold to HTML strong tags
            answer = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", answer)

            # Step 4: Format paragraphs properly
            paragraphs = [p for p in re.split(r"\n\s*\n", answer) if p.strip()]
            formatted_paragraphs = []

            for p in paragraphs:
                # Skip paragraphs that are already HTML elements
                if p.strip().startswith("<") and ">" in p:
                    formatted_paragraphs.append(p)
                    continue

                # Format bullet points
                if re.search(r"^[-•]\s", p, re.MULTILINE):
                    lines = p.split("\n")
                    bullet_list = []
                    for line in lines:
                        if re.match(r"^[-•]\s", line):
                            clean_line = re.sub(r"^[-•]\s", "", line)
                            bullet_list.append(f"<li>{clean_line}</li>")
                    formatted_paragraphs.append(
                        f"<ul class='ai-list'>{''.join(bullet_list)}</ul>"
                    )

                # Format numbered lists
                elif re.search(r"^\d+\.\s", p, re.MULTILINE):
                    lines = p.split("\n")
                    number_list = []
                    for line in lines:
                        if re.match(r"^\d+\.\s", line):
                            clean_line = re.sub(r"^\d+\.\s", "", line)
                            number_list.append(f"<li>{clean_line}</li>")
                    formatted_paragraphs.append(
                        f"<ol class='ai-list'>{''.join(number_list)}</ol>"
                    )

                # Regular paragraph
                else:
                    formatted_paragraphs.append(f"<p>{p}</p>")

            answer = "\n".join(formatted_paragraphs)

            # Step 5: Clean up any special characters or emojis with Bootstrap Icons
            emoji_to_icon = {
                # Weather icons
                "🌤️": "sun",
                "☀️": "sun-fill",
                "🌧️": "cloud-rain",
                "❄️": "snow",
                # Travel icons
                "✈️": "airplane",
                "🛫": "airplane-fill",
                "🚗": "car-front",
                "🏨": "building",
                # UI icons
                "📅": "calendar",
                "👉": "arrow-right-circle-fill",
                "✅": "check-circle-fill",
                "💰": "cash-coin",
                "⭐": "star-fill",
            }

            # Replace emojis with their corresponding Bootstrap icons
            for emoji, icon_name in emoji_to_icon.items():
                css_class = "text-success" if icon_name in ["check-circle-fill"] else ""
                css_class = "text-warning" if icon_name in ["star-fill"] else css_class
                icon_html = f'<i class="bi bi-{icon_name} {css_class}"></i>'
                answer = answer.replace(emoji, f" {icon_html} ")

            # Format the response with proper HTML
            formatted_answer = f"<div class='ai-question mb-3'><strong>Q: {question}</strong></div><div class='ai-answer'>{answer}</div>"

            return jsonify({"response": formatted_answer})
        else:
            return (
                jsonify(
                    {
                        "response": f"<p>Error from AI service: {response.status_code}</p><p>{response.text}</p>"
                    }
                ),
                response.status_code,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "response": f"<p>Sorry, I couldn't process your question: {str(e)}</p>",
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
