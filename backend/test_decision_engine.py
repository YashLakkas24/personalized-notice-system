from app.services.decision_engine import evaluate_student_for_notice

student = {
    "id": "student_1",
    "name": "Alex Kumar",
    "year": 3,
    "branch": "CS",
    "interests": ["Hackathons", "AI/ML", "Coding"],
}

student_2 = {
    "id": "student_2",
    "name": "Pooja Sharma",
    "year": 1,
    "branch": "ME",
    "interests": ["Sports", "Cultural Events"],
}
hackathon_notice = {
    "title": "National AI Hackathon 2026",
    "category": "Hackathons",
    "is_mandatory": False,
    "eligibility": {"branches": ["ALL"], "years": [2, 3]},
    "summary": "Participate in an AI and coding hackathon.",
    "deadline": "2026-09-18",
}


print(evaluate_student_for_notice(student_2, hackathon_notice))
