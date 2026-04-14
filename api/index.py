import os
import json
import re
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# ---------------- CONFIG ----------------
VALID_KEY = "nexxon07" # আপনার নতুন কী
DEVELOPER = "CREATOR SHYAMCHAND | @nexxonhackers"

def check_key():
    key = request.args.get("key")
    return key == VALID_KEY

# ---------------- AUTH TOKENS ----------------
def get_auth_data():
    # Vercel-এ ফাইল পাথ ম্যানেজমেন্ট
    path = os.path.join(os.path.dirname(__file__), '..', 'auth.json')
    if not os.path.exists(path):
        return None
    with open(path, "r") as file:
        return json.load(file)

auth_data = get_auth_data()
if not auth_data:
    # যদি ফাইল না থাকে তবে ডিফল্ট ভ্যালু (সতর্কতা: এটি কাজ না করলে ফাইল চেক করুন)
    E_AUTH = "26289c7e-a943-4d09-a9b6-3a89793abcc0"
    E_AUTH_C = "29"
else:
    E_AUTH = auth_data.get("e-auth")
    E_AUTH_C = auth_data.get("e-auth-c")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "accept": "*/*",
    "e-auth-v": "e1",
    "e-auth": E_AUTH,
    "e-auth-c": E_AUTH_C,
    "e-auth-k": "PgdtSBeR0MumR7fO",
    "Accept-Encoding": "gzip",
    "Host": "api.eyecon-app.com",
    "Connection": "Keep-Alive"
}

# ---------------- HELPERS ----------------
def extract_fb_id(url):
    m = re.search(r'facebook\.com/(?:v[0-9.]+/)?(\d+)/picture', url)
    if m: return m.group(1)
    m2 = re.search(r'facebook\.com/(\d+)/', url)
    if m2: return m2.group(1)
    return None

def parse_names(xml_text):
    try:
        root = ET.fromstring(xml_text)
        names = [elem.text for elem in root.findall(".//name")]
        return names if names else []
    except: return []

# ---------------- EYEcON FUNCTIONS ----------------
def get_pic_data(number):
    url = f"https://api.eyecon-app.com/app/pic?cli={number}&is_callerid=true&size=big&type=0&src=DefaultDialer&cv=vc_613"
    resp = requests.get(url, headers=HEADERS, allow_redirects=False, timeout=10)
    
    if resp.status_code == 302:
        loc = resp.headers.get("Location")
        fb_id = extract_fb_id(loc) if loc else None
        if fb_id:
            return {"facebook_id": fb_id, "fb_url": f"https://facebook.com/{fb_id}", "image": loc}
        return {"image": loc}
    return {"image": "Not found"}

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return jsonify({"status": "Live", "dev": DEVELOPER, "usage": "/lookup?number=91XXXXXXXXXX&key=nexxon07"})

@app.route("/lookup", methods=["GET"])
def lookup():
    if not check_key():
        return jsonify({"error": "Invalid Key! Access Denied."}), 403
    
    number = request.args.get("number")
    if not number:
        return jsonify({"error": "Number parameter is missing"}), 400

    # Eyecon API Calls
    name_resp = requests.get(f"https://api.eyecon-app.com/app/getnames.jsp?cli={number}&lang=en", headers=HEADERS, timeout=10)
    names = parse_names(name_resp.text)
    pic_info = get_pic_data(number)

    return jsonify({
        "status": "success",
        "developer": DEVELOPER,
        "data": {
            "phone": number,
            "names": names,
            "facebook": pic_info.get("fb_url", "No FB Link"),
            "facebook_id": pic_info.get("facebook_id", "N/A"),
            "profile_pic": pic_info.get("image")
        }
    })

# Vercel Handler
app_handler = app
