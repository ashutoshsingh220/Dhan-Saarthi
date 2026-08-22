from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.learning import LearningModule, UserLearningProgress
from app.models.scam import ScamScan
from app.models.user import User
from app.schemas.learning import (
    LearningModuleResponse,
    LearningProgressSummaryResponse,
    LearningRecommendationResponse,
    QuizQuestionPublic,
    QuizResultResponse,
)


class LearningService:
    SEED_MODULES = [
        {
            "module_id": "savings-basics",
            "title": "Savings Basics",
            "description": "Master the fundamentals of saving money and building an emergency financial cushion.",
            "category": "Basics",
            "difficulty": "Beginner",
            "estimated_minutes": 5,
            "lesson_content": {
                "sections": [
                    {
                        "heading": "Why Saving Matters",
                        "body": "Saving money provides peace of mind, financial security, and protection against unexpected life events like emergency medical expenses or temporary job loss.",
                    },
                    {
                        "heading": "The Emergency Fund Rule",
                        "body": "Financial experts recommend keeping at least 3 to 6 months of essential living expenses in a liquid, easily accessible account before taking investment risks.",
                    },
                    {
                        "heading": "Building a Habit",
                        "body": "Treat your savings as a non-negotiable monthly expense. Save first as soon as your income arrives, rather than saving whatever happens to be left over.",
                    },
                ],
                "key_takeaways": [
                    "Aim to build a 3-6 month emergency expense buffer.",
                    "Automate your savings right after receiving monthly income.",
                    "Keep emergency funds in safe, liquid bank accounts.",
                ],
            },
            "quiz_questions": [
                {
                    "id": "sb_q1",
                    "question": "How many months of expenses should ideally be kept in an emergency fund?",
                    "options": ["1 month", "3 to 6 months", "12 to 24 months", "None at all"],
                    "correct_option_index": 1,
                },
                {
                    "id": "sb_q2",
                    "question": "What is the best strategy for building a consistent saving habit?",
                    "options": [
                        "Save whatever money is left at the end of the month",
                        "Save a fixed portion immediately after receiving income",
                        "Spend all money and borrow during emergencies",
                        "Only save when you get a bonus",
                    ],
                    "correct_option_index": 1,
                },
                {
                    "id": "sb_q3",
                    "question": "Where should emergency buffer funds be parked?",
                    "options": [
                        "High-risk volatile assets",
                        "Illiquid real estate properties",
                        "Safe, liquid bank accounts",
                        "Unregulated online schemes",
                    ],
                    "correct_option_index": 2,
                },
            ],
        },
        {
            "module_id": "budgeting",
            "title": "Budgeting Fundamentals",
            "description": "Learn how to track income, manage monthly expenses, and control your cashflow.",
            "category": "Budgeting",
            "difficulty": "Beginner",
            "estimated_minutes": 6,
            "lesson_content": {
                "sections": [
                    {
                        "heading": "Needs vs. Wants",
                        "body": "Categorize your monthly outflow into essential needs (rent, groceries, utilities, debt repayment) and discretionary wants (entertainment, dining out, luxury shopping).",
                    },
                    {
                        "heading": "The 50/30/20 Rule",
                        "body": "A popular framework: allocate 50% of net income to needs, 30% to wants, and 20% to savings and long-term financial goals.",
                    },
                    {
                        "heading": "Tracking Cashflow",
                        "body": "Consistently tracking cashflow prevents accidental overspending and highlights categories where expenses can be optimized.",
                    },
                ],
                "key_takeaways": [
                    "Distinguish clearly between mandatory needs and optional wants.",
                    "Use the 50/30/20 guideline to structure your monthly budget.",
                    "Review spending weekly to catch unexpected leaks early.",
                ],
            },
            "quiz_questions": [
                {
                    "id": "b_q1",
                    "question": "In the 50/30/20 budget framework, what does the 50% allocate to?",
                    "options": ["Discretionary Wants", "Essential Needs", "Investments & Debt", "Entertainment"],
                    "correct_option_index": 1,
                },
                {
                    "id": "b_q2",
                    "question": "Which of the following is considered an essential need?",
                    "options": ["Dining at luxury restaurants", "Rent and monthly utility bills", "Weekend vacation trips", "Designer clothing"],
                    "correct_option_index": 1,
                },
                {
                    "id": "b_q3",
                    "question": "Why is regular cashflow tracking important?",
                    "options": [
                        "It prevents accidental overspending and highlights savings potential",
                        "It guarantees instant high investment returns",
                        "It eliminates the need for emergency funds",
                        "It forces you to stop buying groceries",
                    ],
                    "correct_option_index": 0,
                },
            ],
        },
        {
            "module_id": "credit-loans",
            "title": "Credit & Loans Awareness",
            "description": "Understand credit scores, interest calculations, and responsible borrowing.",
            "category": "Credit",
            "difficulty": "Intermediate",
            "estimated_minutes": 7,
            "lesson_content": {
                "sections": [
                    {
                        "heading": "What is Credit?",
                        "body": "Credit is borrowed capital that allows you to buy now and pay later. Responsible credit usage builds a high credit score, enabling cheaper loan interest rates.",
                    },
                    {
                        "heading": "The High Cost of Debt Traps",
                        "body": "High-interest loans or carrying unpaid credit card balances can rapidly accumulate debt due to compounding interest charges.",
                    },
                    {
                        "heading": "Responsible Borrowing",
                        "body": "Ensure total monthly loan EMIs do not exceed 35-40% of your monthly net income to maintain healthy financial debt capacity.",
                    },
                ],
                "key_takeaways": [
                    "Always pay credit card dues in full before the interest-free due date.",
                    "Keep total EMI load under 40% of your monthly income.",
                    "Avoid high-interest payday or unverified instant loan apps.",
                ],
            },
            "quiz_questions": [
                {
                    "id": "cl_q1",
                    "question": "What is the recommended maximum limit for monthly loan EMI payments?",
                    "options": ["70-80% of net income", "35-40% of net income", "100% of net income", "EMI limits do not matter"],
                    "correct_option_index": 1,
                },
                {
                    "id": "cl_q2",
                    "question": "What happens when you carry an unpaid balance on a credit card?",
                    "options": [
                        "Interest is waived automatically",
                        "High compounding interest fees accumulate on unpaid balances",
                        "Your bank rewards you with bonus points",
                        "Your credit score increases immediately",
                    ],
                    "correct_option_index": 1,
                },
                {
                    "id": "cl_q3",
                    "question": "How does maintaining a good credit score help you financially?",
                    "options": [
                        "It lets you borrow unlimited money without repayment",
                        "It helps secure lower interest rates and easier loan approvals",
                        "It doubles your monthly salary",
                        "It replaces the need for bank accounts",
                    ],
                    "correct_option_index": 1,
                },
            ],
        },
        {
            "module_id": "digital-payment-safety",
            "title": "Digital Payment Safety",
            "description": "Protect your digital transactions, UPI PIN, OTPs, and avoid fraudulent traps.",
            "category": "Safety",
            "difficulty": "Beginner",
            "estimated_minutes": 5,
            "lesson_content": {
                "sections": [
                    {
                        "heading": "The Golden Rule of UPI PIN",
                        "body": "Entering your UPI PIN is ONLY required when SENDING money or checking your bank balance. Receiving money NEVER requires entering your UPI PIN.",
                    },
                    {
                        "heading": "OTP & Credential Protection",
                        "body": "Never share One-Time Passwords (OTPs), CVV numbers, net banking passwords, or transaction PINs with anyone — including bank representatives.",
                    },
                    {
                        "heading": "Verifying Payment Requests",
                        "body": "Be suspicious of urgent money transfer requests, unknown QR codes, or unverified link shorteners claiming to unlock rewards or unblock accounts.",
                    },
                ],
                "key_takeaways": [
                    "Entering UPI PIN means money leaves your bank account.",
                    "Never share OTP, PIN, or CVV with anyone.",
                    "Verify suspicious messages using official bank customer service numbers.",
                ],
            },
            "quiz_questions": [
                {
                    "id": "dps_q1",
                    "question": "When is entering a UPI PIN required?",
                    "options": [
                        "When receiving money from a friend",
                        "Only when sending money or checking account balance",
                        "When accepting a cash prize reward",
                        "When answering a phone call",
                    ],
                    "correct_option_index": 1,
                },
                {
                    "id": "dps_q2",
                    "question": "Should you ever share your OTP or PIN with someone claiming to be a bank official?",
                    "options": [
                        "Yes, if they sound professional",
                        "Yes, if they promise to resolve an account block",
                        "No, legitimate bank officials never ask for OTP or PIN",
                        "Yes, if sent via SMS",
                    ],
                    "correct_option_index": 2,
                },
                {
                    "id": "dps_q3",
                    "question": "What should you do if an unknown sender sends a QR code claiming it will transfer money to you?",
                    "options": [
                        "Scan it and enter your PIN immediately",
                        "Do not scan or enter PIN; scanning unknown QR codes can deduct funds",
                        "Share the QR code with all your contacts",
                        "Forward your bank password to the sender",
                    ],
                    "correct_option_index": 1,
                },
            ],
        },
        {
            "module_id": "investment-basics",
            "title": "Investment Basics",
            "description": "Understand how investments grow wealth, combat inflation, and manage risk.",
            "category": "Investing",
            "difficulty": "Intermediate",
            "estimated_minutes": 7,
            "lesson_content": {
                "sections": [
                    {
                        "heading": "Saving vs. Investing",
                        "body": "Saving protects money for short-term needs, while investing allocates capital to assets expected to grow over time and outperform inflation.",
                    },
                    {
                        "heading": "The Power of Compounding",
                        "body": "Compounding means earning returns on both your initial investment and on accumulated earnings. Starting early gives compounding more time to work.",
                    },
                    {
                        "heading": "Risk and Diversification",
                        "body": "Higher potential returns come with higher volatility. Diversifying across asset classes reduces risk by not putting all your eggs in one basket.",
                    },
                ],
                "key_takeaways": [
                    "Investing helps beat inflation and grow long-term wealth.",
                    "Start early to harness the power of compound interest.",
                    "Diversify across asset classes to manage investment risk.",
                ],
            },
            "quiz_questions": [
                {
                    "id": "ib_q1",
                    "question": "Why is long-term investing important compared to simple cash savings?",
                    "options": [
                        "It guarantees 100% daily profits",
                        "It helps beat inflation and build wealth over time",
                        "Cash savings lose value faster than anything else",
                        "Investing eliminates all financial risk completely",
                    ],
                    "correct_option_index": 1,
                },
                {
                    "id": "ib_q2",
                    "question": "What is compounding in investing?",
                    "options": [
                        "Paying double taxes every year",
                        "Earning returns on both principal investment and previous accumulated earnings",
                        "Borrowing money from friends",
                        "Selling investments at a loss",
                    ],
                    "correct_option_index": 1,
                },
                {
                    "id": "ib_q3",
                    "question": "What does diversification mean in portfolio management?",
                    "options": [
                        "Putting all money into a single stock",
                        "Spreading investments across multiple asset classes to reduce risk",
                        "Keeping money in a single savings account",
                        "Taking maximum risk on unverified schemes",
                    ],
                    "correct_option_index": 1,
                },
            ],
        },
        {
            "module_id": "financial-goals",
            "title": "Smart Financial Goals",
            "description": "Align your savings and investment strategies with specific life milestones.",
            "category": "Goals",
            "difficulty": "Beginner",
            "estimated_minutes": 6,
            "lesson_content": {
                "sections": [
                    {
                        "heading": "Setting Specific Goals",
                        "body": "Define clear financial targets (e.g. Emergency Fund, Home Downpayment, Education) with concrete target amounts and target dates.",
                    },
                    {
                        "heading": "Matching Horizon to Strategy",
                        "body": "Short-term goals (< 3 years) require capital preservation in safe liquid accounts. Long-term goals (> 5 years) can incorporate growth assets.",
                    },
                    {
                        "heading": "Tracking and Adjusting",
                        "body": "Regularly monitor goal progress against monthly required contributions and adjust plans when income or expense dynamics change.",
                    },
                ],
                "key_takeaways": [
                    "Attach target dates and exact amounts to your financial goals.",
                    "Keep short-term goal funds in low-volatility accounts.",
                    "Review progress quarterly and recalculate plans when needed.",
                ],
            },
            "quiz_questions": [
                {
                    "id": "fg_q1",
                    "question": "What is an essential characteristic of a smart financial goal?",
                    "options": [
                        "Vague target with no timeline",
                        "Concrete target amount and specific target date",
                        "Unrealistic amount impossible to achieve",
                        "Copying whatever your neighbor is doing",
                    ],
                    "correct_option_index": 1,
                },
                {
                    "id": "fg_q2",
                    "question": "Where should funds for short-term goals (< 2 years) ideally be kept?",
                    "options": ["Volatile high-risk stocks", "Safe, low-volatility liquid options", "Cryptocurrency bets", "Lottery tickets"],
                    "correct_option_index": 1,
                },
                {
                    "id": "fg_q3",
                    "question": "Why should you periodically review your goal progress?",
                    "options": [
                        "To adjust monthly contributions and verify feasibility as circumstances change",
                        "To cancel all your goals immediately",
                        "To pay extra penalties to the bank",
                        "Goal progress never needs reviewing",
                    ],
                    "correct_option_index": 0,
                },
            ],
        },
    ]

    @classmethod
    def ensure_seeded(cls, db: Session) -> None:
        for m_data in cls.SEED_MODULES:
            existing = db.scalar(select(LearningModule).where(LearningModule.module_id == m_data["module_id"]))
            if not existing:
                module = LearningModule(
                    module_id=m_data["module_id"],
                    title=m_data["title"],
                    description=m_data["description"],
                    category=m_data["category"],
                    difficulty=m_data["difficulty"],
                    estimated_minutes=m_data["estimated_minutes"],
                )
                module.lesson_content = m_data["lesson_content"]
                module.quiz_questions = m_data["quiz_questions"]
                db.add(module)
        db.commit()

    @classmethod
    def get_modules(cls, db: Session, user: User) -> List[LearningModuleResponse]:
        cls.ensure_seeded(db)
        modules = db.scalars(select(LearningModule).order_by(LearningModule.id)).all()
        progress_map = {
            p.module_id: p for p in db.scalars(select(UserLearningProgress).where(UserLearningProgress.user_id == user.id)).all()
        }

        res = []
        for m in modules:
            prog = progress_map.get(m.module_id)
            res.append(
                LearningModuleResponse(
                    module_id=m.module_id,
                    title=m.title,
                    description=m.description,
                    category=m.category,
                    difficulty=m.difficulty,
                    estimated_minutes=m.estimated_minutes,
                    lesson_content=m.lesson_content,
                    status=prog.status if prog else "NOT_STARTED",
                    completed_at=prog.completed_at if prog else None,
                    quiz_score=prog.quiz_score if prog else None,
                )
            )
        return res

    @classmethod
    def get_module_detail(cls, db: Session, user: User, module_id: str) -> Optional[LearningModuleResponse]:
        cls.ensure_seeded(db)
        m = db.scalar(select(LearningModule).where(LearningModule.module_id == module_id))
        if not m:
            return None

        prog = db.scalar(
            select(UserLearningProgress).where(
                UserLearningProgress.user_id == user.id, UserLearningProgress.module_id == module_id
            )
        )

        return LearningModuleResponse(
            module_id=m.module_id,
            title=m.title,
            description=m.description,
            category=m.category,
            difficulty=m.difficulty,
            estimated_minutes=m.estimated_minutes,
            lesson_content=m.lesson_content,
            status=prog.status if prog else "NOT_STARTED",
            completed_at=prog.completed_at if prog else None,
            quiz_score=prog.quiz_score if prog else None,
        )

    @classmethod
    def start_module(cls, db: Session, user: User, module_id: str) -> LearningModuleResponse:
        cls.ensure_seeded(db)
        m = db.scalar(select(LearningModule).where(LearningModule.module_id == module_id))
        if not m:
            raise ValueError(f"Module '{module_id}' not found")

        prog = db.scalar(
            select(UserLearningProgress).where(
                UserLearningProgress.user_id == user.id, UserLearningProgress.module_id == module_id
            )
        )

        if not prog:
            prog = UserLearningProgress(
                user_id=user.id,
                module_id=module_id,
                status="IN_PROGRESS",
                started_at=datetime.now(),
            )
            db.add(prog)
        elif prog.status == "NOT_STARTED":
            prog.status = "IN_PROGRESS"
            prog.started_at = datetime.now()

        db.commit()
        db.refresh(prog)

        return cls.get_module_detail(db, user, module_id)

    @classmethod
    def get_quiz(cls, db: Session, module_id: str) -> List[QuizQuestionPublic]:
        cls.ensure_seeded(db)
        m = db.scalar(select(LearningModule).where(LearningModule.module_id == module_id))
        if not m:
            raise ValueError(f"Module '{module_id}' not found")

        questions = m.quiz_questions
        public_qs = []
        for q in questions:
            public_qs.append(
                QuizQuestionPublic(
                    id=q["id"],
                    question=q["question"],
                    options=q["options"],
                )
            )
        return public_qs

    @classmethod
    def submit_quiz(cls, db: Session, user: User, module_id: str, answers: List[int]) -> QuizResultResponse:
        cls.ensure_seeded(db)
        m = db.scalar(select(LearningModule).where(LearningModule.module_id == module_id))
        if not m:
            raise ValueError(f"Module '{module_id}' not found")

        questions = m.quiz_questions
        total_questions = len(questions)
        if len(answers) != total_questions:
            raise ValueError(f"Expected {total_questions} answers, but received {len(answers)}")

        correct_count = 0
        for idx, q in enumerate(questions):
            user_ans = answers[idx]
            if user_ans == q["correct_option_index"]:
                correct_count += 1

        score_pct = round((correct_count / total_questions) * 100.0, 2)
        passed = score_pct >= 60.0

        prog = db.scalar(
            select(UserLearningProgress).where(
                UserLearningProgress.user_id == user.id, UserLearningProgress.module_id == module_id
            )
        )

        if not prog:
            prog = UserLearningProgress(
                user_id=user.id,
                module_id=module_id,
                status="COMPLETED" if passed else "IN_PROGRESS",
                started_at=datetime.now(),
                completed_at=datetime.now() if passed else None,
                quiz_score=score_pct,
            )
            db.add(prog)
        else:
            prog.quiz_score = score_pct
            if passed:
                prog.status = "COMPLETED"
                prog.completed_at = datetime.now()
            elif prog.status == "NOT_STARTED":
                prog.status = "IN_PROGRESS"

        db.commit()

        if passed:
            feedback = f"Great effort! You answered {correct_count} out of {total_questions} correctly ({score_pct}%). Lesson completed!"
        else:
            feedback = f"You answered {correct_count} out of {total_questions} correctly ({score_pct}%). Review the lesson content and try again."

        return QuizResultResponse(
            score_percentage=score_pct,
            correct_count=correct_count,
            total_questions=total_questions,
            status=prog.status,
            feedback=feedback,
        )

    @classmethod
    def get_progress_summary(cls, db: Session, user: User) -> LearningProgressSummaryResponse:
        cls.ensure_seeded(db)
        all_modules = db.scalars(select(LearningModule)).all()
        total = len(all_modules)

        user_progs = db.scalars(select(UserLearningProgress).where(UserLearningProgress.user_id == user.id)).all()
        completed = sum(1 for p in user_progs if p.status == "COMPLETED")
        in_progress = sum(1 for p in user_progs if p.status == "IN_PROGRESS")

        pct = round((completed / total * 100.0), 1) if total > 0 else 0.0

        return LearningProgressSummaryResponse(
            total_modules=total,
            completed_modules=completed,
            in_progress_modules=in_progress,
            completion_percentage=pct,
        )

    @classmethod
    def get_recommendations(cls, db: Session, user: User) -> List[LearningRecommendationResponse]:
        cls.ensure_seeded(db)
        all_modules = {m.module_id: m for m in db.scalars(select(LearningModule)).all()}
        user_progs = {
            p.module_id: p for p in db.scalars(select(UserLearningProgress).where(UserLearningProgress.user_id == user.id)).all()
        }

        recommendations: List[LearningRecommendationResponse] = []
        added_ids = set()

        # Check Recent Scam Shield Scans
        recent_scams = db.scalars(
            select(ScamScan).where(ScamScan.user_id == user.id).order_by(ScamScan.created_at.desc()).limit(3)
        ).all()
        has_high_scam = any(s.risk_level in ["CRITICAL", "HIGH"] for s in recent_scams)

        if has_high_scam and "digital-payment-safety" in all_modules:
            mod_id = "digital-payment-safety"
            if user_progs.get(mod_id, None) is None or user_progs[mod_id].status != "COMPLETED":
                m = all_modules[mod_id]
                recommendations.append(
                    LearningRecommendationResponse(
                        module_id=m.module_id,
                        title=m.title,
                        description=m.description,
                        reason="Recommended because your recent Scam Shield scans detected high-risk payment threats.",
                        estimated_minutes=m.estimated_minutes,
                    )
                )
                added_ids.add(mod_id)

        # Check Financial Twin & Cashflow
        twin = user.financial_twin
        profile = user.profile
        low_score = twin and twin.financial_health_score < 60
        low_surplus = profile and (float(profile.monthly_income) - float(profile.monthly_expenses)) < 5000

        if (low_score or low_surplus) and "budgeting" in all_modules and "budgeting" not in added_ids:
            if user_progs.get("budgeting", None) is None or user_progs["budgeting"].status != "COMPLETED":
                m = all_modules["budgeting"]
                recommendations.append(
                    LearningRecommendationResponse(
                        module_id=m.module_id,
                        title=m.title,
                        description=m.description,
                        reason="Recommended to help optimize monthly cashflow and boost your Financial Health Score.",
                        estimated_minutes=m.estimated_minutes,
                    )
                )
                added_ids.add("budgeting")

        # Check Financial Goals
        goals = getattr(user, "goals", [])
        has_tight_or_at_risk = any(g.plan and g.plan.feasibility_status in ["AT_RISK", "TIGHT"] for g in goals)

        if has_tight_or_at_risk and "financial-goals" in all_modules and "financial-goals" not in added_ids:
            if user_progs.get("financial-goals", None) is None or user_progs["financial-goals"].status != "COMPLETED":
                m = all_modules["financial-goals"]
                recommendations.append(
                    LearningRecommendationResponse(
                        module_id=m.module_id,
                        title=m.title,
                        description=m.description,
                        reason="Recommended to align monthly savings capacity with your active financial goals.",
                        estimated_minutes=m.estimated_minutes,
                    )
                )
                added_ids.add("financial-goals")

        # Fill defaults if < 2 recommendations
        fallback_order = ["savings-basics", "budgeting", "financial-goals", "digital-payment-safety", "credit-loans", "investment-basics"]
        for mod_id in fallback_order:
            if len(recommendations) >= 3:
                break
            if mod_id not in added_ids and mod_id in all_modules:
                m = all_modules[mod_id]
                prog = user_progs.get(mod_id)
                if not prog or prog.status != "COMPLETED":
                    recommendations.append(
                        LearningRecommendationResponse(
                            module_id=m.module_id,
                            title=m.title,
                            description=m.description,
                            reason="Recommended foundational financial literacy topic to build financial confidence.",
                            estimated_minutes=m.estimated_minutes,
                        )
                    )
                    added_ids.add(mod_id)

        return recommendations
