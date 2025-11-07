from datetime import datetime, timezone

import requests

def get_bus_data():
    apiUrl = "https://api.tfl.gov.uk/StopPoint/490014137W/Arrivals"
    try:
        response = requests.get(apiUrl, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error fetching data...")
        return[]

def parse_utc_time(iso_string):
    try:
        if iso_string.endswith("Z"):
            return datetime.fromisoformat(iso_string.replace("Z", "+00:00")).astimezone(timezone.utc)
        return datetime.fromisoformat(iso_string).astimezone(timezone.utc)
    except Exception:
        return None


def generate_list_item(bus):
    line = bus.get("lineName", "N/A")
    vehicle = bus.get("vehicleId", "Unknown")
    arrival_time = parse_utc_time(bus.get("expectedArrival", ""))
    if arrival_time:
        minutes = round((arrival_time - datetime.now(timezone.utc)).total_seconds() / 60)
        minutes = max(minutes, 0)  # Avoid negative numbers
    else:
        minutes = "N/A"
    return f"<li><strong>{line} - ({vehicle})</strong> arriving in: {minutes} min</li>"

def generate_list_items(sorted_buses):
    if sorted_buses:
        return "\n".join(generate_list_item(bus) for bus in sorted_buses)
    else:
        return "<li>No buses scheduled</li>"

def build_html(buses):
    target_line_name = "SL7"
    now = datetime.now(timezone.utc)
    sl7_buses = [
        b for b in buses
        if b.get("lineName", "").strip() == target_line_name
    ]
    buses_sorted = sorted(sl7_buses, key=lambda bus: bus["expectedArrival"])
    list_items = generate_list_items(buses_sorted)
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Bus Arrivals</title>
        <style>
        body {{ font-family: sans-serif; background: #ffffff; color: #000000; }}
        h2 {{ margin-bottom: 5px; }}
        p {{ font-size: 12px; margin-top: 0; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
        th, td {{ border: 1px solid #000000; padding: 4px; text-align: left; }}
        th {{ background: #dddddd; }}
        </style>
    </head>
    <body>
        <p>Arrivals at stop: <code>Wallington Green / Croydon Road</code> towards Sutton for <strong>SL7</strong>…</p>
        <p>Updated: {now}</p>
        <ul>{list_items}</ul>
        <p><small>Refresh the page to see updates.</small></p>
    </body>
    </html>"""

    return html

if __name__ == "__main__":
    data = get_bus_data()
    html = build_html(data)
    with open("./../index.html", "w", encoding="utf-8") as f:
        f.write(html)
    # print("index.html generated successfully.")
    # print(html)