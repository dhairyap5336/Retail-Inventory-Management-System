from groq import Groq

# Replace with your Groq API key
client = Groq(api_key="GROG_API_KEY")

def generate_explanation(results):

    selected = results[results["Optimal_Stock"] > 0]

    prompt = f"""
Explain in simple business language why the AI selected these products for inventory optimization.

Data:
{selected[['Product','Optimal_Stock','Expected_Profit']]}
"""

    try:

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content

    except Exception:

        # fallback if API fails
        explanation = "AI Decision Summary:\n\n"

        for _, row in selected.iterrows():

            explanation += (
                f"{row['Product']} should be stocked at approximately "
                f"{int(row['Optimal_Stock'])} units because it contributes "
                f"₹{int(row['Expected_Profit'])} expected profit.\n"
            )

        return explanation