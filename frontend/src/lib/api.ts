import type {
  AnalyzeRequest,
  AnalyzeResponse,
} from "@/types/fraud";


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";


export async function checkHealth() {

  const response =
    await fetch(`${API_URL}/health`);

  if (!response.ok) {
    throw new Error(
      `Health check failed: ${response.status}`
    );
  }

  return response.json();
}


export async function analyzeTransaction(
  request: AnalyzeRequest
): Promise<AnalyzeResponse> {

  const response =
    await fetch(`${API_URL}/analyze`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(request),
    });


  if (!response.ok) {

    const errorText =
      await response.text();

    throw new Error(
      `Analysis failed: ${response.status} ${errorText}`
    );

  }


  return response.json();
}