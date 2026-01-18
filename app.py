"""
Legal Notice Generator - Simple Flask API
Works on Pydroid3 and can be deployed
"""

from flask import Flask, request, jsonify
import requests
import datetime
import json

app = Flask(__name__)

# API Key
OPENROUTER_API_KEY = "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"

def call_openrouter_api(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.25,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return None

def build_prompt(data):
    today = datetime.date.today().strftime("%d/%m/%Y")
    invoice_line = f"Invoice/Bill No. {data.get('invoice', '')}" if data.get('invoice') else ""
    
    return f"""You are a senior Indian advocate specializing in consumer law.

Draft a FORMAL LEGAL NOTICE for a consumer dispute.

Date: {today}

Complainant: {data['complainant_name']}
Address: {data['complainant_address']}

Respondent: {data['respondent_name']}
Address: {data['respondent_address']}

Date of Transaction: {data['date_of_cause']}
{invoice_line}
Amount: Rs. {data['amount']}

Facts:
{data['facts']}

Relief:
{data['relief']}

Delivery: {data.get('delivery_mode', 'Registered Post')}

STRUCTURE:
1. "To," then respondent details
2. "Date: {today}"
3. Subject line
4. "Dear Sir/Madam,"
5. Numbered facts
6. NOTICE AND DEMAND section
7. 15-day compliance
8. Consequences
9. Delivery statement
10. Advocate placeholders

Use "deficiency in service" language. NO case citations. NO sections.
Output ONLY the notice text."""

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>Legal Notice Generator</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; text-align: center; }
            input, textarea {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 15px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover { background: #2980b9; }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #ecf0f1;
                border-radius: 5px;
                white-space: pre-wrap;
                display: none;
            }
            .loading {
                text-align: center;
                color: #7f8c8d;
                display: none;
            }
            label { font-weight: bold; color: #34495e; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚖️ Legal Notice Generator</h1>
            <p style="text-align: center; color: #7f8c8d;">Consumer Law - India</p>
            
            <form id="noticeForm">
                <label>Complainant Name:</label>
                <input type="text" id="complainant_name" required>
                
                <label>Complainant Address:</label>
                <input type="text" id="complainant_address" required>
                
                <label>Respondent Name:</label>
                <input type="text" id="respondent_name" required>
                
                <label>Respondent Address:</label>
                <input type="text" id="respondent_address" required>
                
                <label>Date of Purchase (DD/MM/YYYY):</label>
                <input type="text" id="date_of_cause" required>
                
                <label>Amount Paid (₹):</label>
                <input type="text" id="amount" required>
                
                <label>Invoice Number (optional):</label>
                <input type="text" id="invoice">
                
                <label>Facts of Case:</label>
                <textarea id="facts" rows="5" required></textarea>
                
                <label>Relief Sought:</label>
                <textarea id="relief" rows="3" required></textarea>
                
                <button type="submit">Generate Notice</button>
            </form>
            
            <div class="loading" id="loading">
                ⏳ Generating notice... Please wait 10-15 seconds...
            </div>
            
            <div class="result" id="result"></div>
        </div>
        
        <script>
            document.getElementById('noticeForm').onsubmit = async (e) => {
                e.preventDefault();
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('result').style.display = 'none';
                
                const data = {
                    complainant_name: document.getElementById('complainant_name').value,
                    complainant_address: document.getElementById('complainant_address').value,
                    respondent_name: document.getElementById('respondent_name').value,
                    respondent_address: document.getElementById('respondent_address').value,
                    date_of_cause: document.getElementById('date_of_cause').value,
                    amount: document.getElementById('amount').value,
                    invoice: document.getElementById('invoice').value,
                    facts: document.getElementById('facts').value,
                    relief: document.getElementById('relief').value
                };
                
                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    document.getElementById('loading').style.display = 'none';
                    
                    if (result.success) {
                        document.getElementById('result').textContent = result.notice;
                        document.getElementById('result').style.display = 'block';
                    } else {
                        alert('Error: ' + result.error);
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    alert('Error: ' + error.message);
                }
            };
        </script>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        
        # Validate
        required = ['complainant_name', 'respondent_name', 'facts', 'relief']
        for field in required:
            if not data.get(field):
                return jsonify({"success": False, "error": f"Missing {field}"}), 400
        
        # Build prompt
        prompt = build_prompt(data)
        
        # Generate
        notice = call_openrouter_api(prompt)
        
        if notice:
            return jsonify({"success": True, "notice": notice})
        else:
            return jsonify({"success": False, "error": "API failed"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Legal Notice Generator API")
    print("Open in browser: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
    
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)    