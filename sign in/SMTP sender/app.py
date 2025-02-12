import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory storage for API keys and usage limits
api_keys = {}

# Generate API Key Endpoint
@app.route('/generate_api_key', methods=['GET'])
def generate_api_key():
    api_key = str(uuid.uuid4())
    api_keys[api_key] = {'emails_sent': 0}
    return jsonify({'api_key': api_key, 'message': 'API key generated successfully'})

# Send Email Endpoint
@app.route('/send_email', methods=['POST'])
def send_email():
    api_key = request.headers.get('API-Key')
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Invalid API key'}), 403

    # Enforce email limit (10,000 emails per API key)
    if api_keys[api_key]['emails_sent'] >= 10000:
        return jsonify({'error': 'Email limit reached for this API key'}), 403

    # Extract email details from the request
    data = request.json
    from_email = data.get('from_email')
    from_name = data.get('from_name', 'No Name')
    to_emails = data.get('to_emails', [])
    subject = data.get('subject', 'No Subject')
    html_content = data.get('html_content', '')

    # Validate required fields
    if not from_email or not to_emails or not subject or not html_content:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Relay configuration (customized for the API-based approach)
        smtp_server = "localhost"  # Replace with your relay server or localhost for testing
        smtp_port = 25  # Use 25, 587, or any available SMTP port

        # Create the SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)

        # Send email to each recipient
        for email in to_emails:
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))

            # Send the email
            server.sendmail(from_email, email, msg.as_string())
            api_keys[api_key]['emails_sent'] += 1

        server.quit()
        return jsonify({'message': f'{len(to_emails)} emails sent successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    