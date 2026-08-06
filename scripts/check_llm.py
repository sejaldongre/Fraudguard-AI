from src.fraudguard.rag import (
    create_llm_client,
    LLM_MODEL
)


print(
    "Creating Groq client..."
)

client = create_llm_client()


print(
    "Testing LLM connection..."
)


response = (
    client.chat.completions.create(

        model=LLM_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a financial "
                    "fraud analysis assistant."
                )
            },
            {
                "role": "user",
                "content": (
                    "In one sentence, explain "
                    "what payment fraud is."
                )
            }
        ],

        temperature=0.1,

        max_completion_tokens=100
    )
)


answer = (
    response
    .choices[0]
    .message
    .content
)


print("\nLLM Response:\n")

print(answer)
