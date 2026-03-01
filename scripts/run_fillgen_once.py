from app import create_app

app = create_app()
app.debug = True

with app.app_context():
    from routes.fillgen import generate_fill_questions
    resp = generate_fill_questions()
    try:
        data = resp.get_json()
    except Exception:
        data = str(resp)
    import json
    print(json.dumps(data, indent=2, ensure_ascii=False))
