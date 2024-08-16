from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Email
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Subscriber {self.email}>"

# Criação do banco de dados
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        email = request.json.get('email')
        valid = validate_email(email).email

        if Subscriber.query.filter_by(email=valid).first():
            return jsonify({"message": "Email already subscribed"}), 400

        new_subscriber = Subscriber(email=valid)
        db.session.add(new_subscriber)
        db.session.commit()

        return jsonify({"message": "Subscribed successfully!"}), 200

    except EmailNotValidError as e:
        return jsonify({"message": str(e)}), 400

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    try:
        email = request.json.get('email')
        valid = validate_email(email).email

        # Verificando se o email existe no banco de dados
        subscriber = Subscriber.query.filter_by(email=valid).first()
        if subscriber:
            db.session.delete(subscriber)
            db.session.commit()
            return jsonify({"message": "Unsubscribed successfully!"}), 200
        else:
            return jsonify({"message": "Email not found"}), 404

    except EmailNotValidError as e:
        return jsonify({"message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
