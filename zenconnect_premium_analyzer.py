import whisper
import gradio as gr
import re
from datetime import timedelta

# Don't load model at startup - will load based on user selection
model = None
current_model_name = None

def load_model_if_needed(model_name):
    """Load the Whisper model only when needed"""
    global model, current_model_name
    if model is None or current_model_name != model_name:
        print(f"Loading {model_name} model...")
        model = whisper.load_model(model_name)
        current_model_name = model_name
        print(f"{model_name} model loaded successfully!")
    return model

def analyze_zenconnect_quality(transcription, strictness="moderate"):
    """
    Analyze call based on ZenConnect monitoring criteria:
    - Opening (5 points)
    - Handling & Process (20 points)
    - Knowledge & Accuracy (10 points)
    - Communication & Language (10 points)
    - Closing & Next Steps (5 points)
    Total: 50 points
    
    Strictness levels:
    - lenient: More forgiving, gives benefit of doubt
    - moderate: Balanced expectations
    - strict: High standards, less forgiving
    """
    
    # Define strictness multipliers for scoring thresholds
    if strictness == "lenient":
        threshold_multiplier = 0.7  # Lower thresholds = easier to score
        bonus_multiplier = 1.3  # More generous bonuses
    elif strictness == "strict":
        threshold_multiplier = 1.3  # Higher thresholds = harder to score
        bonus_multiplier = 0.7  # Less generous bonuses
    else:  # moderate
        threshold_multiplier = 1.0
        bonus_multiplier = 1.0
    
    text_lower = transcription.lower()
    scores = {}
    detailed_feedback = {}
    
    # === OPENING (5 points) ===
    opening_score = 0
    opening_details = []
    
    # Check for greeting (max 2 points) - Apply strictness
    greetings = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'thank you for calling', 'thanks for calling']
    greeting_found = any(greeting in text_lower[:200] for greeting in greetings)
    
    if strictness == "lenient":
        # Lenient: Any greeting gets full points
        if greeting_found:
            opening_score += 2 * bonus_multiplier
            opening_details.append("✓ Professional greeting detected")
        else:
            opening_score += 0.5  # Still give some credit
            opening_details.append("◐ No clear greeting, but being lenient")
    elif strictness == "strict":
        # Strict: Must have professional greeting
        if greeting_found and ('thank you for calling' in text_lower[:200] or 'thanks for calling' in text_lower[:200]):
            opening_score += 2 * bonus_multiplier
            opening_details.append("✓ Professional greeting detected")
        elif greeting_found:
            opening_score += 0.5
            opening_details.append("◐ Basic greeting - needs more professionalism")
        else:
            opening_details.append("✗ No clear greeting found")
    else:  # moderate
        if greeting_found and ('thank you for calling' in text_lower[:200] or 'thanks for calling' in text_lower[:200]):
            opening_score += 2
            opening_details.append("✓ Professional greeting detected")
        elif greeting_found:
            opening_score += 1
            opening_details.append("◐ Basic greeting, could be more professional")
        else:
            opening_details.append("✗ No clear greeting found")
    
    # Check for verification/identity (max 1.5 points) - Apply strictness
    verify_phrases = ['may i have your', 'can i get your', 'verify', 'confirm your', 'your name', 'account number', 'system id']
    verify_count = sum(1 for phrase in verify_phrases if phrase in text_lower)
    
    if strictness == "lenient":
        if verify_count >= 1:
            opening_score += 1.5 * bonus_multiplier
            opening_details.append("✓ Identity verification attempted")
        else:
            opening_score += 0.5
            opening_details.append("◐ Minimal verification, being lenient")
    elif strictness == "strict":
        if verify_count >= 2:
            opening_score += 1.5 * bonus_multiplier
            opening_details.append("✓ Identity verification attempted")
        elif verify_count == 1:
            opening_score += 0.5
            opening_details.append("◐ Insufficient verification")
        else:
            opening_details.append("✗ No verification detected")
    else:  # moderate
        if verify_count >= 2:
            opening_score += 1.5
            opening_details.append("✓ Identity verification attempted")
        elif verify_count == 1:
            opening_score += 0.75
            opening_details.append("◐ Minimal verification")
        else:
            opening_details.append("✗ No verification detected")
    
    # Check for purpose identification (max 1.5 points) - STRICTER
    purpose_phrases = ['how can i help', 'what can i do', 'how may i assist', "what's the reason", 'what brings you', 'how can i assist']
    if any(phrase in text_lower[:300] for phrase in purpose_phrases):
        opening_score += 1.5
        opening_details.append("✓ Purpose of call identified")
    else:
        opening_score += 0
        opening_details.append("✗ Purpose not clearly identified")
    
    scores['opening'] = round(opening_score, 1)
    detailed_feedback['opening'] = opening_details
    
    # === HANDLING & PROCESS (20 points) ===
    handling_score = 0
    handling_details = []
    
    # Active listening (max 5 points) - MUCH STRICTER
    listening_phrases = ['i understand', 'i see', 'got it', 'okay', 'right', 'i hear you', 'that makes sense']
    listening_count = sum(text_lower.count(phrase) for phrase in listening_phrases)
    if listening_count >= 8:
        handling_score += 5
        handling_details.append("✓ Strong active listening demonstrated")
    elif listening_count >= 5:
        handling_score += 3
        handling_details.append("◐ Adequate active listening")
    elif listening_count >= 2:
        handling_score += 1.5
        handling_details.append("◐ Minimal active listening")
    else:
        handling_details.append("✗ Limited active listening cues")
    
    # Empathy & rapport (max 4 points) - STRICTER
    empathy_phrases = ['sorry', 'apologize', 'understand your frustration', 'appreciate your patience', 'i can imagine', 'i would feel']
    empathy_count = sum(text_lower.count(phrase) for phrase in empathy_phrases)
    if empathy_count >= 4:
        handling_score += 4
        handling_details.append("✓ Excellent empathy shown")
    elif empathy_count >= 2:
        handling_score += 2
        handling_details.append("◐ Some empathy demonstrated")
    elif empathy_count >= 1:
        handling_score += 1
        handling_details.append("◐ Minimal empathy")
    else:
        handling_details.append("✗ Limited empathy expressed")
    
    # Clarifying questions (max 3 points) - STRICTER
    question_count = text_lower.count('?')
    clarifying_words = ['what', 'when', 'where', 'how', 'which', 'could you', 'can you']
    clarify_count = sum(text_lower.count(word) for word in clarifying_words)
    if clarify_count >= 8 and question_count >= 4:
        handling_score += 3
        handling_details.append("✓ Good clarifying questions asked")
    elif clarify_count >= 5 and question_count >= 2:
        handling_score += 1.5
        handling_details.append("◐ Some clarifying questions")
    elif clarify_count >= 2:
        handling_score += 0.5
        handling_details.append("◐ Minimal clarification")
    else:
        handling_details.append("✗ No clarifying questions detected")
    
    # Hold/transfer protocol (max 4 points) - SAME
    hold_phrases = ['place you on hold', 'hold for a moment', 'one moment', 'give me a moment', 'bear with me']
    transfer_phrases = ['transfer you', 'connect you', 'specialist', 'another team']
    has_hold = any(phrase in text_lower for phrase in hold_phrases)
    has_transfer = any(phrase in text_lower for phrase in transfer_phrases)
    
    if has_hold:
        handling_score += 2
        handling_details.append("✓ Proper hold procedure used")
    if has_transfer:
        handling_score += 2
        handling_details.append("✓ Transfer protocol followed")
    if not has_hold and not has_transfer:
        handling_score += 4  # No hold/transfer needed
        handling_details.append("✓ No hold/transfer required")
    
    # Process adherence (max 4 points) - STRICTER
    process_phrases = ['let me check', 'looking into', 'reviewing', 'checking', 'pulling up', 'i will', 'i am going to']
    process_count = sum(text_lower.count(phrase) for phrase in process_phrases)
    if process_count >= 3:
        handling_score += 4
        handling_details.append("✓ Followed troubleshooting process")
    elif process_count >= 1:
        handling_score += 2
        handling_details.append("◐ Basic process followed")
    else:
        handling_score += 0
        handling_details.append("✗ Process adherence unclear")
    
    scores['handling'] = round(min(handling_score, 20), 1)
    detailed_feedback['handling'] = handling_details
    
    # === KNOWLEDGE & ACCURACY (10 points) ===
    knowledge_score = 0
    knowledge_details = []
    
    # Correct information provided (max 5 points)
    confidence_phrases = ['the solution is', 'what you need to do', 'here is how', 'the correct', 'the way to']
    technical_terms = ['system', 'software', 'hardware', 'setting', 'configuration', 'update', 'restart', 'troubleshoot']
    
    has_confidence = any(phrase in text_lower for phrase in confidence_phrases)
    tech_count = sum(text_lower.count(term) for term in technical_terms)
    
    if has_confidence and tech_count >= 3:
        knowledge_score += 5
        knowledge_details.append("✓ Clear, confident technical guidance")
    elif has_confidence or tech_count >= 2:
        knowledge_score += 3
        knowledge_details.append("◐ Adequate technical information")
    else:
        knowledge_score += 1
        knowledge_details.append("◐ Limited technical detail")
    
    # Resources referenced (max 3 points)
    resource_phrases = ['manual', 'documentation', 'guide', 'article', 'knowledge base', 'faq', 'support page']
    if any(phrase in text_lower for phrase in resource_phrases):
        knowledge_score += 3
        knowledge_details.append("✓ Referenced appropriate resources")
    else:
        knowledge_details.append("◐ No external resources mentioned")
    
    # Safety/compliance (max 2 points)
    safety_phrases = ['data protection', 'privacy', 'security', 'backup', 'save your work', 'important to']
    if any(phrase in text_lower for phrase in safety_phrases):
        knowledge_score += 2
        knowledge_details.append("✓ Safety/compliance considerations mentioned")
    else:
        knowledge_score += 1
        knowledge_details.append("◐ Basic safety awareness")
    
    scores['knowledge'] = round(min(knowledge_score, 10), 1)
    detailed_feedback['knowledge'] = knowledge_details
    
    # === COMMUNICATION & LANGUAGE (10 points) ===
    comm_score = 0
    comm_details = []
    word_count = len(transcription.split())
    
    # Clear language (max 4 points) - MUCH STRICTER on filler words
    filler_words = len(re.findall(r'\b(um|uh|like|you know|basically|actually|sort of|kind of)\b', text_lower))
    if word_count > 0:
        filler_ratio = filler_words / word_count
        if filler_ratio < 0.01:  # Less than 1% filler words
            comm_score += 4
            comm_details.append("✓ Very clear, minimal filler words")
        elif filler_ratio < 0.025:  # Less than 2.5%
            comm_score += 2.5
            comm_details.append("◐ Mostly clear speech")
        elif filler_ratio < 0.05:  # Less than 5%
            comm_score += 1
            comm_details.append("◐ Some filler words present")
        else:
            comm_score += 0
            comm_details.append("✗ Excessive filler words")
    
    # Grammar & professionalism (max 3 points) - STRICTER
    professional_phrases = ['please', 'thank you', 'appreciate', 'certainly', 'absolutely', 'of course']
    prof_count = sum(text_lower.count(phrase) for phrase in professional_phrases)
    if prof_count >= 7:
        comm_score += 3
        comm_details.append("✓ Excellent professional language")
    elif prof_count >= 4:
        comm_score += 2
        comm_details.append("◐ Professional language used")
    elif prof_count >= 2:
        comm_score += 1
        comm_details.append("◐ Basic professionalism")
    else:
        comm_score += 0
        comm_details.append("✗ Limited professional language")
    
    # Tone & pace (max 3 points) - STRICTER on sentence structure
    sentence_count = len([s for s in transcription.split('.') if s.strip()])
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    if 12 <= avg_sentence_length <= 18:  # Narrower optimal range
        comm_score += 3
        comm_details.append("✓ Good pace and tone (estimated)")
    elif 10 <= avg_sentence_length <= 22:
        comm_score += 1.5
        comm_details.append("◐ Acceptable pace")
    else:
        comm_score += 0.5
        comm_details.append("◐ Pace may need adjustment")
    
    scores['communication'] = round(min(comm_score, 10), 1)
    detailed_feedback['communication'] = comm_details
    
    # === CLOSING & NEXT STEPS (5 points) ===
    closing_score = 0
    closing_details = []
    
    # Resolution confirmation (max 2 points) - STRICTER
    resolution_phrases = ['did that help', 'does that work', 'is that clear', 'solve', 'resolved', 'fixed', 'working now', 'does that answer']
    resolution_count = sum(1 for phrase in resolution_phrases if phrase in text_lower[-300:])
    if resolution_count >= 2:
        closing_score += 2
        closing_details.append("✓ Confirmed resolution")
    elif resolution_count >= 1:
        closing_score += 1
        closing_details.append("◐ Minimal resolution confirmation")
    else:
        closing_details.append("✗ No resolution confirmation")
    
    # Additional help offered (max 1.5 points) - STRICTER
    offer_phrases = ['anything else', 'help you with anything', 'other questions', 'further assistance', 'anything else i can help']
    if any(phrase in text_lower[-300:] for phrase in offer_phrases):
        closing_score += 1.5
        closing_details.append("✓ Offered additional assistance")
    else:
        closing_details.append("✗ No offer for additional help")
    
    # Follow-up mentioned (max 1.5 points) - STRICTER
    followup_phrases = ['follow up', 'call back', 'email you', 'reach out', 'contact you', 'ticket number', 'reference number']
    followup_count = sum(1 for phrase in followup_phrases if phrase in text_lower)
    if followup_count >= 2:
        closing_score += 1.5
        closing_details.append("✓ Follow-up plan established")
    elif followup_count >= 1:
        closing_score += 0.75
        closing_details.append("◐ Basic follow-up mentioned")
    else:
        closing_details.append("✗ No specific follow-up mentioned")
    
    scores['closing'] = round(closing_score, 1)
    detailed_feedback['closing'] = closing_details
    
    # Calculate total
    total_score = sum(scores.values())
    percentage = (total_score / 50) * 100
    
    # Collect flagged issues for highlighting
    flagged_issues = []
    
    # Check for critical issues
    if scores['opening'] < 3:
        flagged_issues.append({'category': 'Opening', 'issue': 'Poor opening - missing greeting, verification, or purpose', 'severity': 'high'})
    if scores['handling'] < 12:
        flagged_issues.append({'category': 'Handling', 'issue': 'Inadequate handling - needs improvement in listening, empathy, or process', 'severity': 'high'})
    if scores['knowledge'] < 6:
        flagged_issues.append({'category': 'Knowledge', 'issue': 'Technical knowledge concerns - unclear or incorrect information', 'severity': 'high'})
    if scores['communication'] < 6:
        flagged_issues.append({'category': 'Communication', 'issue': 'Communication problems - excessive filler words or unclear speech', 'severity': 'medium'})
    if scores['closing'] < 3:
        flagged_issues.append({'category': 'Closing', 'issue': 'Poor closing - no resolution confirmation or follow-up', 'severity': 'high'})
    
    # Determine category based on percentage
    if percentage >= 90:
        category = "Excellent"
        category_emoji = "🟢"
    elif percentage >= 80:
        category = "Good"
        category_emoji = "🟢"
    elif percentage >= 70:
        category = "Satisfactory"
        category_emoji = "🟡"
    elif percentage >= 60:
        category = "Needs Improvement"
        category_emoji = "🟠"
    else:
        category = "Unsatisfactory"
        category_emoji = "🔴"
    
    return scores, total_score, percentage, category, category_emoji, detailed_feedback, flagged_issues

def format_html_report(scores, total, percentage, category, category_emoji, detailed_feedback, flagged_issues, duration_str, word_count, speaking_rate, language):
    """Format a beautiful HTML report"""
    
    # Determine color scheme based on score
    if percentage >= 90:
        score_color = "#16a34a"
        bg_gradient = "linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)"
    elif percentage >= 80:
        score_color = "#16a34a"
        bg_gradient = "linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)"
    elif percentage >= 70:
        score_color = "#eab308"
        bg_gradient = "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)"
    else:
        score_color = "#ef4444"
        bg_gradient = "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)"
    
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #4C799B 0%, #3a5f7a 100%); padding: 30px; border-radius: 20px; color: white;">
        
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; color: white;">
                ZenConnect Quality Analysis
            </h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Powered by AI-Enhanced Monitoring</p>
        </div>
        
        <!-- Overall Score Card -->
        <div style="background: {bg_gradient}; border-radius: 16px; padding: 30px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <div style="text-align: center;">
                <div style="font-size: 18px; color: #64748b; font-weight: 600; margin-bottom: 15px;">OVERALL SCORE</div>
                <div style="font-size: 72px; font-weight: 900; color: {score_color}; line-height: 1; margin-bottom: 10px;">
                    {total:.1f}<span style="font-size: 36px; opacity: 0.7;">/50</span>
                </div>
                <div style="font-size: 28px; font-weight: 700; color: {score_color}; margin-bottom: 15px;">
                    {percentage:.1f}%
                </div>
                <div style="display: inline-block; background: white; padding: 10px 25px; border-radius: 50px; font-size: 20px; font-weight: 700; color: {score_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    {category_emoji} {category}
                </div>
            </div>
        </div>
        
        <!-- Stats Grid -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px;">
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Duration</div>
                <div style="font-size: 24px; font-weight: 700;">⏱️ {duration_str}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Words</div>
                <div style="font-size: 24px; font-weight: 700;">📝 {word_count}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">WPM</div>
                <div style="font-size: 24px; font-weight: 700;">🗣️ {speaking_rate:.0f}</div>
            </div>
            <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; text-align: center;">
                <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Language</div>
                <div style="font-size: 24px; font-weight: 700;">🌐 {language.upper()}</div>
            </div>
        </div>
        
        <!-- Category Breakdown -->
        <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 16px; padding: 25px; margin-bottom: 25px;">
            <h2 style="margin: 0 0 20px 0; font-size: 20px; font-weight: 700;">📊 Performance Breakdown</h2>
            
            {create_score_bar("Opening", scores['opening'], 5)}
            {create_score_bar("Handling & Process", scores['handling'], 20)}
            {create_score_bar("Knowledge & Accuracy", scores['knowledge'], 10)}
            {create_score_bar("Communication & Language", scores['communication'], 10)}
            {create_score_bar("Closing & Next Steps", scores['closing'], 5)}
        </div>
        
        <!-- Flagged Issues Section -->
        {create_flagged_issues_section(flagged_issues) if flagged_issues else ''}
        
        <!-- Detailed Feedback -->
        <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 16px; padding: 25px;">
            <h2 style="margin: 0 0 20px 0; font-size: 20px; font-weight: 700;">💡 Detailed Feedback</h2>
            
            {create_feedback_section("Opening", detailed_feedback['opening'])}
            {create_feedback_section("Handling & Process", detailed_feedback['handling'])}
            {create_feedback_section("Knowledge & Accuracy", detailed_feedback['knowledge'])}
            {create_feedback_section("Communication & Language", detailed_feedback['communication'])}
            {create_feedback_section("Closing & Next Steps", detailed_feedback['closing'])}
        </div>
        
    </div>
    """
    
    return html

def create_flagged_issues_section(flagged_issues):
    """Create a prominent section showing flagged issues"""
    if not flagged_issues:
        return ""
    
    html = """
    <div style="background: rgba(239, 68, 68, 0.15); backdrop-filter: blur(10px); border-radius: 16px; padding: 25px; margin-bottom: 25px; border: 2px solid #ef4444;">
        <h2 style="margin: 0 0 20px 0; font-size: 20px; font-weight: 700; color: #fee2e2;">🚨 Flagged Issues - Requires Attention</h2>
    """
    
    for issue in flagged_issues:
        severity_color = "#ef4444" if issue['severity'] == 'high' else "#f59e0b"
        severity_bg = "rgba(239, 68, 68, 0.2)" if issue['severity'] == 'high' else "rgba(245, 158, 11, 0.2)"
        severity_label = "HIGH PRIORITY" if issue['severity'] == 'high' else "MEDIUM PRIORITY"
        
        html += f"""
        <div style="background: {severity_bg}; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid {severity_color};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                <span style="font-weight: 700; font-size: 16px; color: white;">⚠️ {issue['category']}</span>
                <span style="background: {severity_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;">{severity_label}</span>
            </div>
            <div style="color: #fee2e2; line-height: 1.5;">{issue['issue']}</div>
        </div>
        """
    
    html += """
    </div>
    """
    
    return html

def create_score_bar(label, score, max_score):
    """Create a visual score bar"""
    percentage = (score / max_score) * 100
    
    if percentage >= 90:
        bar_color = "#16a34a"
    elif percentage >= 80:
        bar_color = "#3b82f6"
    elif percentage >= 70:
        bar_color = "#eab308"
    else:
        bar_color = "#ef4444"
    
    return f"""
    <div style="margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="font-weight: 600; font-size: 15px;">{label}</span>
            <span style="font-weight: 700; font-size: 15px;">{score:.1f}/{max_score}</span>
        </div>
        <div style="background: rgba(255,255,255,0.3); border-radius: 50px; height: 12px; overflow: hidden;">
            <div style="background: {bar_color}; width: {percentage}%; height: 100%; border-radius: 50px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """

def create_feedback_section(title, feedback_items):
    """Create a feedback section"""
    items_html = ""
    for item in feedback_items:
        icon = "✓" if item.startswith("✓") else ("◐" if item.startswith("◐") else "✗")
        
        if icon == "✓":
            color = "#16a34a"
            bg = "rgba(22, 163, 74, 0.1)"
        elif icon == "◐":
            color = "#eab308"
            bg = "rgba(234, 179, 8, 0.1)"
        else:
            color = "#ef4444"
            bg = "rgba(239, 68, 68, 0.1)"
        
        items_html += f"""
        <div style="background: {bg}; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {color};">
            <span style="color: {color}; font-weight: 700; margin-right: 8px;">{icon}</span>
            <span style="color: white;">{item[2:]}</span>
        </div>
        """
    
    return f"""
    <div style="margin-bottom: 20px;">
        <div style="font-weight: 700; font-size: 16px; margin-bottom: 12px; opacity: 0.95;">▸ {title}</div>
        {items_html}
    </div>
    """

def generate_recommendations_html(scores, percentage):
    """Generate recommendations in HTML format"""
    
    if percentage >= 90:
        bg_color = "rgba(22, 163, 74, 0.15)"
        border_color = "#16a34a"
        icon = "🌟"
        title = "OUTSTANDING PERFORMANCE"
        message = "Continue demonstrating this exceptional level of service excellence."
    elif percentage >= 80:
        bg_color = "rgba(59, 130, 246, 0.15)"
        border_color = "#3b82f6"
        icon = "⭐"
        title = "STRONG PERFORMANCE"
        message = "Great work! Minor refinements will elevate you to excellence."
    else:
        bg_color = "rgba(234, 179, 8, 0.15)"
        border_color = "#eab308"
        icon = "⚠️"
        title = "IMPROVEMENT OPPORTUNITIES"
        message = "Focus on the areas below to enhance your performance."
    
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #4C799B 0%, #3a5f7a 100%); padding: 30px; border-radius: 20px; color: white;">
        
        <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 20px; border-radius: 12px; margin-bottom: 25px;">
            <div style="font-size: 20px; font-weight: 700; margin-bottom: 10px;">{icon} {title}</div>
            <div style="font-size: 16px; opacity: 0.9;">{message}</div>
        </div>
    """
    
    # Specific recommendations
    recommendations = []
    
    if scores['opening'] < 4:
        recommendations.append({
            'title': 'Opening Improvements',
            'icon': '🚪',
            'items': [
                'Provide a warm, professional greeting',
                'Always verify customer identity properly',
                'Clearly identify and acknowledge call purpose'
            ]
        })
    
    if scores['handling'] < 16:
        recommendations.append({
            'title': 'Handling & Process',
            'icon': '🔧',
            'items': [
                'Demonstrate more active listening cues',
                'Show empathy and build stronger rapport',
                'Ask clarifying questions to understand fully',
                'Follow proper hold and transfer protocols'
            ]
        })
    
    if scores['knowledge'] < 8:
        recommendations.append({
            'title': 'Knowledge & Accuracy',
            'icon': '📚',
            'items': [
                'Provide confident, detailed technical solutions',
                'Reference knowledge base articles when applicable',
                'Address safety and compliance considerations'
            ]
        })
    
    if scores['communication'] < 8:
        recommendations.append({
            'title': 'Communication Skills',
            'icon': '💬',
            'items': [
                'Reduce use of filler words (um, uh, like)',
                'Maintain professional language throughout',
                'Adjust pace for optimal clarity'
            ]
        })
    
    if scores['closing'] < 4:
        recommendations.append({
            'title': 'Closing & Follow-Up',
            'icon': '✅',
            'items': [
                'Always confirm the issue is resolved',
                'Offer additional assistance proactively',
                'Establish clear follow-up plans with customer'
            ]
        })
    
    for rec in recommendations:
        html += f"""
        <div style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border-radius: 12px; padding: 20px; margin-bottom: 15px;">
            <div style="font-size: 18px; font-weight: 700; margin-bottom: 15px;">{rec['icon']} {rec['title']}</div>
            <ul style="margin: 0; padding-left: 20px;">
        """
        
        for item in rec['items']:
            html += f'<li style="margin-bottom: 8px; line-height: 1.5;">{item}</li>'
        
        html += """
            </ul>
        </div>
        """
    
    # Action recommendation
    if percentage < 70:
        action_bg = "rgba(239, 68, 68, 0.2)"
        action_text = "📌 RECOMMENDED ACTION: Coaching Session Required"
    elif percentage < 80:
        action_bg = "rgba(234, 179, 8, 0.2)"
        action_text = "📌 RECOMMENDED ACTION: Additional Training Recommended"
    else:
        action_bg = "rgba(22, 163, 74, 0.2)"
        action_text = "📌 RECOMMENDED ACTION: Continue Current Performance"
    
    html += f"""
        <div style="background: {action_bg}; backdrop-filter: blur(10px); border-radius: 12px; padding: 20px; text-align: center; font-size: 18px; font-weight: 700;">
            {action_text}
        </div>
        
    </div>
    """
    
    return html

def transcribe_and_analyze_zenconnect(audio_file, model_choice, strictness_choice, progress=gr.Progress()):
    """Main function to transcribe and analyze using ZenConnect criteria"""
    
    if audio_file is None:
        return "Please upload an audio file first.", "", ""
    
    try:
        # Map model choice to model name
        model_map = {
            "Fast (Tiny - ~1min for 5min audio)": "tiny",
            "Balanced (Small - ~2min for 5min audio)": "small", 
            "Accurate (Base - ~3min for 5min audio)": "base"
        }
        
        # Map strictness to multiplier
        strictness_map = {
            "Lenient (Generous scoring - Training friendly)": "lenient",
            "Moderate (Balanced expectations)": "moderate",
            "Strict (High standards - Quality focused)": "strict"
        }
        
        model_name = model_map.get(model_choice, "small")
        strictness = strictness_map.get(strictness_choice, "moderate")
        
        # Progress: Starting transcription
        progress(0, desc=f"Loading {model_name} model...")
        
        # Load the appropriate model
        current_model = load_model_if_needed(model_name)
        
        # Transcribe
        progress(0.2, desc="Transcribing audio with Whisper...")
        result = current_model.transcribe(audio_file, word_timestamps=True)
        
        progress(0.5, desc="Audio transcription complete!")
        
        transcription = result["text"]
        language = result["language"]
        duration = result.get("duration", 0)
        word_count = len(transcription.split())
        
        # Calculate statistics
        duration_str = str(timedelta(seconds=int(duration))).split('.')[0]
        speaking_rate = (word_count / duration * 60) if duration > 0 else 0
        
        # Analyze using ZenConnect criteria
        progress(0.7, desc="Analyzing call quality...")
        scores, total, percentage, category, category_emoji, detailed_feedback, flagged_issues = analyze_zenconnect_quality(transcription, strictness)
        
        # Format HTML reports
        progress(0.85, desc="Generating reports...")
        quality_html = format_html_report(scores, total, percentage, category, category_emoji, detailed_feedback, flagged_issues,
                                          duration_str, word_count, speaking_rate, language)
        
        recommendations_html = generate_recommendations_html(scores, percentage)
        
        # Format transcript with timestamps and issue flags
        transcript_html = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; padding: 25px; border-radius: 16px;">
            <h3 style="margin: 0 0 10px 0; color: #0f172a; font-size: 20px;">📝 Timestamped Transcript</h3>
            <div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #4C799B;">
                <div style="font-size: 13px; color: #64748b;">
                    <strong>Flag Legend:</strong> 
                    <span style="margin-left: 10px;">🔴 High Priority Issue</span>
                    <span style="margin-left: 10px;">🟠 Medium Priority</span>
                    <span style="margin-left: 10px;">🟢 Good Section</span>
                </div>
            </div>
        """
        
        total_duration = duration
        
        for i, segment in enumerate(result["segments"]):
            start_time = str(timedelta(seconds=int(segment['start']))).split('.')[0]
            end_time = str(timedelta(seconds=int(segment['end']))).split('.')[0]
            segment_text = segment['text'].lower()
            
            # Determine if this segment should be flagged
            flag = None
            flag_reason = ""
            border_color = "#4C799B"
            bg_color = "white"
            
            # Check opening (first 20% of call)
            if segment['start'] < (total_duration * 0.2):
                greetings = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'thank you for calling']
                verify_phrases = ['may i have', 'can i get', 'verify', 'confirm your', 'your name']
                
                has_greeting = any(g in segment_text for g in greetings)
                has_verify = any(v in segment_text for v in verify_phrases)
                
                if not has_greeting and i < 2:
                    flag = "🔴"
                    flag_reason = "Missing Greeting"
                    border_color = "#ef4444"
                    bg_color = "#fef2f2"
                elif not has_verify and i < 3 and scores['opening'] < 3:
                    flag = "🟠"
                    flag_reason = "No Verification Detected"
                    border_color = "#f59e0b"
                    bg_color = "#fffbeb"
            
            # Check for excessive filler words throughout
            filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually']
            filler_count = sum(segment_text.count(f' {word} ') for word in filler_words)
            word_count_segment = len(segment['text'].split())
            
            if word_count_segment > 10 and filler_count / word_count_segment > 0.15:
                if not flag:  # Don't override existing flags
                    flag = "🟠"
                    flag_reason = "Excessive Filler Words"
                    border_color = "#f59e0b"
                    bg_color = "#fffbeb"
            
            # Check for empathy/professionalism issues
            negative_phrases = ['whatever', "don't care", "not my problem", "can't help"]
            if any(phrase in segment_text for phrase in negative_phrases):
                flag = "🔴"
                flag_reason = "Unprofessional Language"
                border_color = "#ef4444"
                bg_color = "#fef2f2"
            
            # Check closing (last 20% of call)
            if segment['start'] > (total_duration * 0.8):
                resolution_phrases = ['did that help', 'does that work', 'is that clear', 'resolved', 'fixed']
                followup_phrases = ['anything else', 'further assistance', 'follow up', 'call back']
                
                has_resolution = any(r in segment_text for r in resolution_phrases)
                has_followup = any(f in segment_text for f in followup_phrases)
                
                if has_resolution or has_followup:
                    if not flag:  # Mark good sections
                        flag = "🟢"
                        flag_reason = "Good Closing"
                        border_color = "#16a34a"
                        bg_color = "#f0fdf4"
                elif scores['closing'] < 3 and i == len(result["segments"]) - 1:
                    flag = "🔴"
                    flag_reason = "Poor Closing - No Resolution or Follow-up"
                    border_color = "#ef4444"
                    bg_color = "#fef2f2"
            
            # Build the segment HTML with flags
            flag_badge = ""
            if flag:
                flag_badge = f'<span style="background: {border_color}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; margin-left: 10px;">{flag} {flag_reason}</span>'
            
            transcript_html += f"""
            <div style="background: {bg_color}; padding: 15px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid {border_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-size: 13px; color: #64748b; font-weight: 600; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                    <span>[{start_time} → {end_time}]</span>
                    {flag_badge}
                </div>
                <div style="color: #0f172a; line-height: 1.6;">
                    {segment['text']}
                </div>
            </div>
            """
        
        transcript_html += "</div>"
        
        progress(1.0, desc="Analysis complete!")
        
        return quality_html, recommendations_html, transcript_html
        
    except Exception as e:
        error_html = f"""
        <div style="padding: 30px; background: #fee2e2; border-radius: 16px; color: #991b1b;">
            <h3>❌ Error Processing Audio</h3>
            <p>An error occurred while processing your audio file:</p>
            <p><strong>{str(e)}</strong></p>
            <p>Please make sure:</p>
            <ul>
                <li>The file is a valid audio format (MP3, WAV, M4A, etc.)</li>
                <li>The file is not corrupted</li>
                <li>The file is not too large (try under 25MB)</li>
            </ul>
        </div>
        """
        return error_html, "", ""

# Custom CSS for the interface
custom_css = """
#main-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.gradio-container {
    max-width: 1400px !important;
}

#audio-upload {
    border: 3px dashed rgba(255,255,255,0.3) !important;
    background: rgba(255,255,255,0.1) !important;
    border-radius: 20px !important;
    padding: 40px !important;
}

#analyze-btn {
    background: linear-gradient(135deg, #4C799B 0%, #3a5f7a 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    padding: 20px 40px !important;
    border-radius: 50px !important;
    box-shadow: 0 10px 30px rgba(76, 121, 155, 0.4) !important;
    transition: transform 0.2s !important;
}

#analyze-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 15px 40px rgba(76, 121, 155, 0.6) !important;
}

.output-html {
    border-radius: 20px !important;
    overflow: hidden !important;
}
"""

# Create the interface
with gr.Blocks(css=custom_css, theme=gr.themes.Soft(), title="ZenConnect Call Analyzer") as interface:
    
    gr.HTML("""
    <div style="position: relative; text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #4C799B 0%, #3a5f7a 100%); border-radius: 20px; margin-bottom: 30px; color: white;">
        <img src="data:image/png;base64,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" alt="NeuroOptimal Logo" style="position: absolute; top: 20px; right: 20px; height: 80px; background: white; padding: 10px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h1 style="margin: 0; font-size: 48px; font-weight: 900; letter-spacing: -1px; text-shadow: 0 4px 12px rgba(0,0,0,0.2); color: white;">
            ZenConnect Call Analyzer
        </h1>
        <p style="margin: 15px 0 0 0; font-size: 20px; opacity: 0.95; font-weight: 500;">
            AI-Powered Quality Monitoring System
        </p>
        <div style="margin-top: 20px; padding: 15px 25px; background: rgba(255,255,255,0.2); backdrop-filter: blur(10px); border-radius: 50px; display: inline-block; font-size: 15px; font-weight: 600;">
            Upload • Analyze • Improve
        </div>
    </div>
    """)
    
    with gr.Row():
        audio_input = gr.Audio(
            type="filepath", 
            label="🎵 Upload Your Call Recording",
            elem_id="audio-upload"
        )
    
    with gr.Row():
        with gr.Column():
            model_selector = gr.Dropdown(
                choices=[
                    "Fast (Tiny - ~1min for 5min audio)",
                    "Balanced (Small - ~2min for 5min audio)",
                    "Accurate (Base - ~3min for 5min audio)"
                ],
                value="Balanced (Small - ~2min for 5min audio)",
                label="🎚️ Select Processing Speed",
                info="Fast = quicker but less accurate | Accurate = slower but more precise"
            )
        
        with gr.Column():
            strictness_selector = gr.Dropdown(
                choices=[
                    "Lenient (Generous scoring - Training friendly)",
                    "Moderate (Balanced expectations)",
                    "Strict (High standards - Quality focused)"
                ],
                value="Moderate (Balanced expectations)",
                label="⚖️ Scoring Strictness",
                info="Lenient = More forgiving | Strict = Higher expectations"
            )
    
    with gr.Row():
        analyze_btn = gr.Button(
            "🚀 Analyze Call Quality",
            variant="primary",
            size="lg",
            elem_id="analyze-btn"
        )
    
    # Status message area
    status_output = gr.Textbox(
        label="Status",
        value="Ready to analyze. Upload an audio file and click the button above.",
        interactive=False,
        visible=True
    )
    
    with gr.Row():
        quality_output = gr.HTML(label="Quality Report", elem_classes="output-html")
    
    with gr.Row():
        recommendations_output = gr.HTML(label="Recommendations", elem_classes="output-html")
    
    with gr.Row():
        transcript_output = gr.HTML(label="Transcript", elem_classes="output-html")
    
    gr.HTML("""
    <div style="text-align: center; padding: 30px; background: rgba(76, 121, 155, 0.1); border-radius: 16px; margin-top: 30px; color: #475569;">
        <h3 style="margin: 0 0 15px 0; color: #4C799B; font-size: 20px;">📋 Scoring Methodology</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #4C799B; margin-bottom: 5px;">Opening</div>
                <div style="font-size: 24px; font-weight: 900; color: #1e293b;">5 pts</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #4C799B; margin-bottom: 5px;">Handling & Process</div>
                <div style="font-size: 24px; font-weight: 900; color: #1e293b;">20 pts</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #4C799B; margin-bottom: 5px;">Knowledge</div>
                <div style="font-size: 24px; font-weight: 900; color: #1e293b;">10 pts</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #4C799B; margin-bottom: 5px;">Communication</div>
                <div style="font-size: 24px; font-weight: 900; color: #1e293b;">10 pts</div>
            </div>
            <div style="background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <div style="font-weight: 700; color: #4C799B; margin-bottom: 5px;">Closing</div>
                <div style="font-size: 24px; font-weight: 900; color: #1e293b;">5 pts</div>
            </div>
        </div>
        <p style="margin: 25px 0 0 0; font-size: 14px; font-style: italic;">
            ⚡ Powered by OpenAI Whisper + ZenConnect Quality Standards
        </p>
    </div>
    """)
    
    analyze_btn.click(
        fn=transcribe_and_analyze_zenconnect,
        inputs=[audio_input, model_selector, strictness_selector],
        outputs=[quality_output, recommendations_output, transcript_output],
        show_progress=True
    )

# Launch
if __name__ == "__main__":
    interface.launch(share=False, server_name="127.0.0.1", server_port=7860)