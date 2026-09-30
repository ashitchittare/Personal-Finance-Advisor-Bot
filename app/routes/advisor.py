from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, AIChatMessage
from app.services.ai_advisor import generate_ai_response
from app.services.analytics import get_financial_summary

advisor_bp = Blueprint('advisor', __name__, url_prefix='/advisor')

@advisor_bp.route('/', methods=['GET'])
@login_required
def index():
    messages = AIChatMessage.query.filter_by(user_id=current_user.id).order_by(AIChatMessage.created_at.asc()).all()
    summary = get_financial_summary(current_user.id)
    return render_template('advisor/index.html', messages=messages, summary=summary)


@advisor_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    user_prompt = data.get('message', '').strip()

    if not user_prompt:
        return jsonify({'error': 'Message content cannot be empty.'}), 400

    # Save user message to database
    user_msg = AIChatMessage(
        user_id=current_user.id,
        role='user',
        message=user_prompt
    )
    db.session.add(user_msg)
    db.session.commit()

    # Fetch recent history
    history = AIChatMessage.query.filter_by(user_id=current_user.id).order_by(AIChatMessage.created_at.desc()).limit(10).all()
    history.reverse()

    # Generate response
    ai_response_text = generate_ai_response(current_user, user_prompt, conversation_history=history)

    # Save assistant message to database
    assistant_msg = AIChatMessage(
        user_id=current_user.id,
        role='assistant',
        message=ai_response_text
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'user_message': user_msg.to_dict(),
        'assistant_message': assistant_msg.to_dict()
    })


@advisor_bp.route('/clear', methods=['POST'])
@login_required
def clear_history():
    AIChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('AI Advisor chat history cleared.', 'info')
    return redirect(url_for('advisor.index'))
