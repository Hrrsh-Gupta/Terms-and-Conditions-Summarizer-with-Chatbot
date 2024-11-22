from groq import Groq
import os

def run_model(text,summ_model):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "api_error"
        
    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=summ_model,
        messages=[
            {"role": "system", "content": "Generate only the abstractive summary of these terms and conditions capturing every small detail. Don't include disclaimers."},
            {"role": "user", "content": text}
        ],
        temperature=0.5,
         # Adjust as needed to control summary length
        top_p=1,
        stream=False
    )
    # db.add_query(summ_model)

    return completion.choices[0].message.content


def generate_api_summary(text):

    models_list =[
    ("llama3-8b-8192", 30000),
    ("llama-3.1-8b-instant", 20000),
    ("gemma2-9b-it", 15000)
    ]

    summary = "Cannnot generate summary at this moment, Try again in a minute."

    for model,val in models_list:
        try:
            limit = int(val/1.2)
            summary = run_model(text[:limit], model)
            break
        except Exception:
            pass

    return summary

