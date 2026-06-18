import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    mail.init_app(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        
        from app.models import Workshop
        if Workshop.query.count() == 0:
            seed_workshops()

    return app

def seed_workshops():
    from app.models import Workshop

    initial_workshops = [
        Workshop(
            title="Kagan's Cooperative Learning",
            title_ar="كاجان للتعلم التعاوني",
            description="Introduce teachers to Kagan cooperative learning strategies to increase student engagement and participation. Participants will explore practical Kagan structures that promote collaboration, equal participation, and active learning in the classroom, while building effective teamwork and communication skills among students.",
            description_ar="تعريف المعلمين باستراتيجيات كاجان للتعلم التعاوني لزيادة مشاركة الطلاب. سيكتشف المشاركون هياكل كاجان العملية التي تعزز التعاون والمشاركة المتساوية والتعلم النشط، مع بناء مهارات العمل الجماعي والتواصل الفعال بين الطلاب.",
            instructor="Ghada Naimi & Ghinwa Moawad",
            tech_stack="Cooperative Learning Principles, Kagan Structures, Student Engagement Techniques, Teamwork Skills",
            icon_class="fa-people-group",
            color_class="workshop-purple"
        ),
        Workshop(
            title="Assessment for Learning (AFL)",
            title_ar="التقويم من أجل التعلم",
            description="Enhance teachers' ability to use Assessment for Learning (AFL) strategies to assess student understanding, provide meaningful feedback, and improve student achievement. Differentiate between assessment of learning and assessment for learning, and experience practical AFL strategies for immediate classroom use.",
            description_ar="تعزيز قدرة المعلمين على استخدام استراتيجيات التقويم من أجل التعلم لتقييم فهم الطلاب وتقديم تغذية راجعة هادفة وتحسين تحصيلهم. التمييز بين تقويم التعلم والتقويم من أجل التعلم، وتجربة استراتيجيات AFL العملية للاستخدام الفوري في الفصل.",
            instructor="Haneen Alshraida & Mohamed Abouelmagd",
            tech_stack="AFL Principles, Questioning Techniques, Success Criteria, Exit Tickets, Peer Assessment, Feedback",
            icon_class="fa-chart-line",
            color_class="workshop-blue"
        ),
        Workshop(
            title="Build Your Platform",
            title_ar="ابني منصتك التعليمية",
            description="By the end of the workshop, teachers will be able to build their own educational platforms using AI-powered no-code tools.",
            description_ar="بنهاية الورشة، سيكون المعلمون قادرين على بناء منصاتهم التعليمية باستخدام أدوات الذكاء الاصطناعي التي لا تتطلب برمجة.",
            instructor="Wassim Zouari",
            tech_stack="AI Basics, Prompting Techniques, No-Code Tools",
            icon_class="fa-laptop-code",
            color_class="workshop-green"
        ),
        Workshop(
            title="Lesson Remix: Teach One, Reach All",
            title_ar="ريميكس الدرس: درّس واحداً، وصل للجميع",
            description="By the end of the session, teachers will be able to use the SCAMPER framework to adapt existing activities and make them more accessible, challenging, engaging, or inclusive.",
            description_ar="بنهاية الجلسة، سيكون المعلمون قادرين على استخدام إطار SCAMPER لتكييف الأنشطة وجعلها أكثر سهولة وتحدياً وتفاعلاً وشمولاً.",
            instructor="Shaimaa Esmail",
            tech_stack="SCAMPER Framework, Differentiation Strategies, Lesson Adaptation",
            icon_class="fa-lightbulb",
            color_class="workshop-orange"
        ),
        Workshop(
            title="From Active to Passive: High-Impact Teaching Strategies",
            title_ar="من التعلم السلبي إلى النشط: استراتيجيات تدريس عالية التأثير",
            description="By the end of the workshop, participants will identify and commit to using one active learning strategy in their teaching.",
            description_ar="بنهاية الورشة، سيحدد المشاركون استراتيجية تعلم نشط واحدة ويلتزمون باستخدامها في تدريسهم.",
            instructor="Yara Raslan & Dalia Al Sous",
            tech_stack="Active vs Passive Learning, Student Engagement, Interactive Techniques, Collaborative Learning, Classroom Implementation",
            icon_class="fa-chalkboard-teacher",
            color_class="workshop-pink"
        )
    ]

    for ws in initial_workshops:
        db.session.add(ws)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()