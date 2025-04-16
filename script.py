import streamlit as st
import json
from types import SimpleNamespace
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

with open('input.json', 'r') as file:
    input_data = json.load(file)

# API URL
url = "https://api.web.myhq.in/meeting-room/web/list-slug"

# Make POST request
try:
    response = requests.post(url, json=input_data)
    response.raise_for_status()  # Raise if status code is not 2xx
    data = response.json()

    # OPTIONAL: Save a copy for debugging
    with open("live_response.json", "w") as f:
        json.dump(data, f, indent=2)

    # Validate expected structure
    if "data" in data and "workspaces" in data["data"]:
        st.success("✅ API response is valid!")
        st.write("Workspaces found:", len(data["data"]["workspaces"]))
    else:
        st.warning("⚠️ Response structure unexpected!")
        st.json(data)

except requests.exceptions.RequestException as e:
    st.error(f"❌ Request failed: {e}")
    data = None
except json.JSONDecodeError:
    st.error("❌ Failed to parse JSON response")
    st.text(response.text)
    data = None
    
    
    
    
def extract_workspace_details(workspace_data: dict, input_data: dict, max_results: int = 5) -> list:
    """
    Extracts and returns a list of dictionaries with workspace details.
    
    Args:
        workspace_data (dict): The full response data containing workspaces.
        input_data (dict): The input data containing filters like duration.
        max_results (int): Number of top workspaces to extract.

    Returns:
        list: A list of dictionaries containing detailed workspace info.
    """

    # Get duration from input filters with fallback
    duration = input_data.get("selectedFilters", {}).get("DATE_DURATION_TIME", {}).get("DURATION", 1)

    results = []

    workspaces = workspace_data.get("data", {}).get("workspaces", [])
    if not workspaces:
        st.warning("No workspaces found in data.")
        return results

    for i in range(min(max_results, len(workspaces))):
        workspace = workspaces[i]

        # Safe access to workspace-level fields
        name = workspace.get('name', 'N/A')
        building_name = workspace.get('buildingName', 'N/A')
        location = f"{workspace.get('location', '')}, {workspace.get('region', '')}"
        city = workspace.get('city', 'N/A')
        space_type = workspace.get('spaceType', 'N/A')

        meetingroomworkspace = workspace.get('meetingroomworkspace', {})
        timings = meetingroomworkspace.get('timings', 'N/A')
        status = meetingroomworkspace.get('status', 'N/A')

        inventories = workspace.get('meetingroominventories', [])
        if not inventories:
            continue  # skip this workspace if no inventories

        inventory = inventories[0]
        obj = SimpleNamespace(**inventory)

        capacity = getattr(obj, 'capacity', 0)
        pricePerHour = getattr(obj, 'pricePerHour', 0)
        totalPrice = pricePerHour * duration

        # Handle photos array
        photo_urls = [img.get('url') for img in getattr(obj, 'images', []) if 'url' in img]

        # Link building
        inventory_group = workspace.get('meetingroominventorygroup', {})
        booking_type = inventory_group.get('bookingType', 'instant')
        next_available_date = inventory_group.get('nextAvailableDate', 'today')
        slug = workspace.get('slug', '')

        amenities = "Wifi, TV(with HDMI), Whiteboard, Tea & Coffee (Unlimited on self service)"
        link = f"https://myhq.in/meeting-room/{slug}?capacity={capacity}&bookingType={booking_type}&date={next_available_date}"

        # Add to results
        results.append({
            "name": name,
            "location": location,
            "city": city,
            "timings": timings,
            "status": status,
            "capacity": capacity,
            "pricePerHour": pricePerHour,
            "duration": duration,
            "totalPrice": totalPrice,
            "amenities": amenities,
            "link": link,
            "photos": photo_urls
        })

        # Optional UI display (remove/comment out if running headless or using this purely as a function)
        st.title(name)
        st.subheader(building_name)
        st.text(f"Location: {location}")
        st.text(f"City: {city}")
        st.text(f"Workspace Type: {space_type}")
        st.text(f"Timings: {timings}")
        st.text(f"Status: {status}")
        st.text(f"Capacity: {capacity}")
        st.text(f"Price per hour: ₹{pricePerHour}")
        st.text(f"Duration: {duration}")
        st.text(f"Total Price: ₹{totalPrice}")
        st.text(f"Amenities Included: {amenities}")
        st.text(f"Link: {link}")

        for url in photo_urls:
            st.image(url, caption="Meeting Room", use_container_width=True)

    return results

def send_workspace_email(results, sender_email, receiver_email, input_data: dict, app_password, timings, cc_email=None):
    city = input_data["selectedFilters"]["CITY"].title()
    capacity = input_data["selectedFilters"]["CAPACITY"]
    raw_date = input_data["selectedFilters"]["DATE_DURATION_TIME"]["BOOKING_DATE"]

    # Convert date to '8th April 2025' format
    dt = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    day = dt.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    formatted_date = dt.strftime(f"%-d{suffix} %B %Y")

    msg = MIMEMultipart()
    msg['Subject'] = 'Workspace Options from myHQ'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    if cc_email:
        msg['Cc'] = cc_email

    workspace_blocks = ""
    for i, res in enumerate(results, 1):
        workspace = res["name"]
        address = f'{res["location"]}, {res["city"]}'
        meeting_room = f'{res["capacity"]}-Seater Room'
        hours = res["duration"]
        price_per_hour = res["pricePerHour"]
        total_price = res["totalPrice"]
        amenities = res.get("amenities", "Amenities not listed.")
        photo_links = res.get("photos", [])
        link = res.get("link", "#")

        # Create photo section
        photos_html = "".join(
            f'<img src="{photo}" alt="Room Photo" style="width:200px; height:auto; margin-right:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:8px;" />'
            for photo in photo_links
        )

        price_table = f"""
        <table style="border-collapse: collapse; width: 100%;">
          <tr style="background-color: #0072CE; color: white;">
            <th style="border: 1px solid black; padding: 8px;">Meeting Room</th>
            <th style="border: 1px solid black; padding: 8px;">Total no. of hours</th>
            <th style="border: 1px solid black; padding: 8px;">Per hour price (₹)</th>
            <th style="border: 1px solid black; padding: 8px;">Total Price (₹)</th>
          </tr>
          <tr>
            <td style="border: 1px solid black; padding: 8px;">1</td>
            <td style="border: 1px solid black; padding: 8px;">{hours}</td>
            <td style="border: 1px solid black; padding: 8px;">{price_per_hour}</td>
            <td style="border: 1px solid black; padding: 8px;">{total_price}</td>
          </tr>
        </table>
        """

        block = f"""
        <p><strong>Workspace Details {i:02}:</strong><br>
        Workspace: {workspace}<br>
        Address: {address}<br>
        Meeting Room: {meeting_room}<br>
        <a href="{link}">View Workspace</a><br>
        <strong>Price:</strong></p>

        {price_table}

        <p><strong>Amenities Included:</strong> {amenities}</p>

        <p><strong>Photos:</strong><br>{photos_html}</p>
        """

        workspace_blocks += block

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <p>Hi Kuwar,</p>

    <p>It was nice connecting with you over the call. Thank you for sharing your requirements with us. We are glad you chose us to fulfil your workspace needs. As discussed, I am sharing the complete details below with the options for your reference.</p>

    <p><strong>Reconfirming Requirements</strong><br>
    Dates: {formatted_date}<br>
    Timings: {timings}<br>
    Location: {city}<br>
    No. of Pax: {capacity}</p>

    {workspace_blocks}

    <p><strong>Brief intro about myHQ:</strong><br>
    We, at myHQ, are helping individuals and teams work more productively in this new normal of remote working through our tech-enabled flexible workspace solutions. Instead of bringing the employee to the office, we help you take the office to the employee! myHQ is the largest coworking marketplace with over 800+ coworking spaces across the country.</p>

    <p><strong>Meeting Rooms:</strong> Hold your client meetings, workshops or get your team to present in our fully-serviced meeting rooms. Book on-demand by the hour, and ensure your meeting runs smoothly. It is cheaper than even a cup of coffee in some places – starting at ₹250 per seat per day, available across India!</p>

    <p>Website Link: <a href="https://www.myhq.in">Click here to find your desired meeting room</a></p>

    <p><strong>Why corporates choose us:</strong></p>
    <ul>
    <li>Access to 200+ meeting rooms across India</li>
    <li>Pay-Per-Use pricing (e.g., WeWork from ₹250/hour/person)</li>
    <li>No fixed monthly rental</li>
    <li>Free unlimited WiFi, Tea/Coffee</li>
    <li>No lock-in, deposit, or minimum commitment</li>
    </ul>

    <p><strong>Some of our clients:</strong> Meesho, VTION, Khalsa Aid, Ask Media, Transfive, Squadstack, Sennheiser, Mother Dairy</p>

    <p>Hope this helps! Feel free to call me at +91-9266777965. We'd be happy to assist you further. :)</p>

    <p>Best regards,<br>
    Ayaan Gautam<br>
    Associate - Sales (myHQ)<br>
    Upflex Anarock India Pvt. Ltd.<br>
    7th Floor, Building No. 9B, DLF Cyber City, Phase III, Gurgaon 122002<br>
    M: +91-9266777965<br>
    W: <a href="https://www.myhq.in">www.myhq.in</a></p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, "html"))

    # Prepare full recipient list
    to_list = [receiver_email]
    if cc_email:
        if isinstance(cc_email, str):
            cc_list = [email.strip() for email in cc_email.split(",")]
        elif isinstance(cc_email, list):
            cc_list = cc_email
        else:
            cc_list = []
        to_list += cc_list
    else:
        cc_list = []

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_list, msg.as_string())

    print("Email sent successfully!")

    
    


if data:
    results = extract_workspace_details(data,input_data,5)
    sender_email = "ayaan.gautam@myhq.in"
    receiver_email = "ayaangautam@gmail.com"
    cc_email = "kuwarjain394@gmail.com"
    app_password = 'jmzq bmmu jhmo aviw'

    timings = "10:00 AM to 5:00 PM"
    send_workspace_email(results, sender_email, receiver_email ,input_data, app_password,timings, cc_email)
