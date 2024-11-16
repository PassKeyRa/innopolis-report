from flask import Flask, jsonify, request
from postgres import PostgresDB
from conv_fetcher import ConvFetcher
from math_calculator import calculate
import os
import logging

logger = logging.getLogger(__name__)

def create_app(db_host: str, db_database: str, db_user: str, db_password: str, db_port: int = 5432, math_dir: str = '../math'):
    app = Flask(__name__)
    
    # Initialize database connection
    db = PostgresDB(
        host=db_host,
        database=db_database,
        user=db_user,
        password=db_password
    )
    database_url = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}'

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'poll-exporter'
        }), 200

    @app.route('/api/v3/reports', methods=['GET'])
    def get_reports():
        try:
            report_id = request.args.get('report_id')
            chain = request.args.get('chain')
            if not report_id or not chain:
                return jsonify({"error": "Missing required parameters"}), 400
                
            # Simply check if we have this report
            conversation = db.get_conversation_by_address_and_chain(report_id, chain)
            if not conversation:
                return jsonify({"error": "Report not found or not generated"}), 404

            math_data = db.get_math_data(int(conversation['conversation_id']))
            if not math_data:
                return jsonify({"error": "No report generated"}), 404
                
            return jsonify([{
                "report_id": report_id,
                "created": 0,
                "modified": 0,
                "conversation_id": conversation['conversation_id']
            }])
                
        except Exception as e:
            logger.exception(f"Error getting reports: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/v3/pca2', methods=['GET'])
    def get_math_pca2():
        try:
            conversation_id = request.args.get('conversation_id')
            if not conversation_id:
                return jsonify({"error": "Missing conversation_id parameter"}), 400
                
            math_data = db.get_math_data(int(conversation_id))
            if not math_data:
                return jsonify({"error": "No report generated"}), 404
                
            return jsonify(math_data)
            
        except Exception as e:
            logger.exception(f"Error getting math data: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/v3/conversations', methods=['GET'])
    def get_conversation():
        try:
            conversation_id = request.args.get('conversation_id')
            if not conversation_id:
                return jsonify({"error": "Missing conversation_id parameter"}), 400
                
            conv_data = db.get_conversation(int(conversation_id))
            if not conv_data:
                return jsonify({"error": "Conversation not found"}), 404
                
            return jsonify(conv_data)
            
        except Exception as e:
            logger.exception(f"Error getting conversation: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/v3/comments', methods=['GET'])
    def get_comments():
        try:
            conversation_id = request.args.get('conversation_id')
            if not conversation_id:
                return jsonify({"error": "Missing conversation_id parameter"}), 400
                
            comments = db.get_comments(int(conversation_id))
            return jsonify(comments)
            
        except Exception as e:
            logger.exception(f"Error getting comments: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/v3/create_report', methods=['GET'])
    def create_report():
        try:
            report_id = request.args.get('report_id')
            chain = request.args.get('chain')
            
            if not report_id or not chain:
                return jsonify({"error": "Missing required parameters"}), 400
                
            # Start async task
            logger.info(f"Checking if conversation exists for {report_id}")
            conversation = db.get_conversation_by_address_and_chain(report_id, chain)
            if not conversation:
                # Fetch from chain and store
                logger.info(f"Fetching conversation from {chain} for {report_id}")
                fetcher = ConvFetcher(chain)
                conv_data = fetcher.fetch(report_id)
                conversation_id = db.add_conversation_data_from_dict(conv_data)
            else:
                conversation_id = conversation['conversation_id']

            logger.info(f"Checking if math data exists for {conversation_id}")
            math_data = db.get_math_data(int(conversation_id))
            if not math_data:
                # Generate math data
                logger.info(f"Generating math data for {conversation_id}")
                calculate(database_url, conversation_id, working_dir=math_dir)
                calculate(database_url, conversation_id, working_dir=math_dir)
            
            logger.info(f"Report generation completed for {conversation_id}")
            return {"status": "completed", "conversation_id": conversation_id}
            
        except Exception as e:
            logger.exception(f"Error initiating report generation: {e}")
            return jsonify({"error": str(e)}), 500
    
    return app