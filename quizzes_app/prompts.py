"""Verbatim prompt templates.

The Gemini prompt is copied unchanged from `docs/quizly-kurzanleitung.md`.
Rewrapping it would corrupt the JSON example it embeds, so this module is
exempt from the line-length rule and holds no logic.
"""

QUIZ_PROMPT_TEMPLATE = """Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    },
    ...
    (exactly 10 questions)
  ]
}

Requirements:

- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.

Transcript:
"""
