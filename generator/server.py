from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'poll-exporter'
        }), 200

    return app
