"""
Small test harness to exercise AI client summarize/suggest functions locally.
Run after setting `GEMINI_API_KEY` in the environment.

Usage (PowerShell):
  $env:GEMINI_API_KEY="your_key_here"; python tools/test_ai_client.py

This script creates simple in-memory objects that mimic the attributes the
AI client expects and prints the results.
"""
from types import SimpleNamespace
from datetime import datetime
from app.ai.ai_client import ai_client


def make_decision():
    return SimpleNamespace(
        id=123,
        text="Migrate our messaging queue to a managed cloud service",
        proposer_name="alice",
        status="approved",
        created_at=datetime.utcnow(),
        approval_threshold=60
    )


def make_votes():
    return [
        SimpleNamespace(vote_type='approve', is_anonymous=False),
        SimpleNamespace(vote_type='approve', is_anonymous=False),
        SimpleNamespace(vote_type='reject', is_anonymous=False),
    ]


if __name__ == '__main__':
    print("AI client initialized:", getattr(ai_client, 'initialized', False))
    print("AI model object present:", getattr(ai_client, 'model', None) is not None)

    decision = make_decision()
    votes = make_votes()

    print('\n--- Running summarize_decision() ---')
    summary = ai_client.summarize_decision(decision, votes)
    print('Summary result:')
    print(summary)

    print('\n--- Running suggest_next_steps() ---')
    suggestions = ai_client.suggest_next_steps(decision, votes)
    print('Suggestions result:')
    print(suggestions)
