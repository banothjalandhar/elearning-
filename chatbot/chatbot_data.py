# chatbot/chatbot_data.py

CHATBOT_DATA = {
    "default_messages": [
        "Welcome! How can I help you today?",
        "1. Courses",
        "2. Fees",
        "3. Batch Timings",
        "4. Contact Admin"
    ],
    "options": {
        "Courses": {
            "questions": {
                "What courses do you offer?": "We offer Python, Django, React, and DevOps courses.",
                "Is there a certification?": "Yes, we provide certificates after course completion."
            }
        },
        "Fees": {
            "questions": {
                "What is the course fee?": "Course fees vary: Python - 10k, Django - 12k, DevOps - 15k.",
                "Is there any discount?": "Yes, we provide early bird and group discounts."
            }
        },
        "Batch Timings": {
            "questions": {
                "What are the batch timings?": "Morning: 8AM-10AM, Evening: 6PM-8PM"
            }
        },
        "Contact Admin": {
            "questions": {
                "I need more info": "You can contact admin via email: admin@codewithjalandhar.com or WhatsApp: +91XXXXXXXXXX"
            }
        }
    }
}
