from flask import Flask, render_template, request, redirect, flash
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'apocrypha_secret_key'  # Needed for flash messages

EMAIL_TO = 'ansh.riyal@nyu.edu'
EMAIL_FROM = 'no-reply@apocrypha.org'  # Placeholder, not used unless SMTP is set up

# Helper function to send email (prints to console as placeholder)
def send_email(subject, body):
    print(f"\n--- EMAIL TO: {EMAIL_TO} ---\nSUBJECT: {subject}\nBODY:\n{body}\n--- END EMAIL ---\n")
    # To enable real email, configure SMTP and uncomment below:
    # msg = MIMEText(body)
    # msg['Subject'] = subject
    # msg['From'] = EMAIL_FROM
    # msg['To'] = EMAIL_TO
    # with smtplib.SMTP('localhost') as server:
    #     server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/vision')
def vision():
    return render_template('vision.html')

@app.route('/join')
def join():
    return render_template('join.html')

@app.route('/invest')
def invest():
    return render_template('invest.html')

@app.route('/karma')
def karma():
    return render_template('karma.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Form handlers
@app.route('/submit_suggestion', methods=['POST'])
def submit_suggestion():
    suggestion = request.form.get('suggestion')
    email = request.form.get('email')
    send_email('New Suggestion', f"Suggestion: {suggestion}\nEmail: {email}")
    flash('Thank you for your suggestion!')
    return redirect('/')

@app.route('/submit_manifesto_feedback', methods=['POST'])
def submit_manifesto_feedback():
    feedback = request.form.get('feedback')
    email = request.form.get('email')
    send_email('Manifesto Feedback', f"Feedback: {feedback}\nEmail: {email}")
    flash('Thank you for your feedback!')
    return redirect('/vision')

@app.route('/submit_join', methods=['POST'])
def submit_join():
    interest = request.form.get('interest')
    email = request.form.get('email')
    send_email('Join Request', f"Interest: {interest}\nEmail: {email}")
    flash('Thank you for joining! We will be in touch.')
    return redirect('/join')

@app.route('/submit_micro_investor', methods=['POST'])
def submit_micro_investor():
    amount = request.form.get('amount')
    email = request.form.get('email')
    send_email('Micro-Investor Interest', f"Amount: {amount}\nEmail: {email}")
    flash('Thank you for your interest!')
    return redirect('/invest')

@app.route('/submit_institutional_investor', methods=['POST'])
def submit_institutional_investor():
    org = request.form.get('org')
    email = request.form.get('email')
    message = request.form.get('message')
    send_email('Institutional Investor Interest', f"Org: {org}\nEmail: {email}\nMessage: {message}")
    flash('Thank you for reaching out!')
    return redirect('/invest')

@app.route('/submit_karma_suggestion', methods=['POST'])
def submit_karma_suggestion():
    suggestion = request.form.get('karma_suggestion')
    email = request.form.get('email')
    send_email('Karma/Ethics Suggestion', f"Suggestion: {suggestion}\nEmail: {email}")
    flash('Thank you for your suggestion!')
    return redirect('/karma')

@app.route('/submit_blog', methods=['POST'])
def submit_blog():
    content = request.form.get('blog_content')
    email = request.form.get('email')
    send_email('Blog Submission', f"Content: {content}\nEmail: {email}")
    flash('Thank you for your submission!')
    return redirect('/blog')

@app.route('/submit_faq', methods=['POST'])
def submit_faq():
    question = request.form.get('faq_question')
    email = request.form.get('email')
    send_email('FAQ Question', f"Question: {question}\nEmail: {email}")
    flash('Thank you for your question!')
    return redirect('/faq')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    message = request.form.get('message')
    email = request.form.get('email')
    send_email('Contact Form', f"Message: {message}\nEmail: {email}")
    flash('Thank you for reaching out!')
    return redirect('/contact')

if __name__ == '__main__':
    app.run(debug=True) 