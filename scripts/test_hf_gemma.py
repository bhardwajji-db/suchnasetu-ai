"""
SuchnaSetu AI — Hugging Face Inference Providers Verification Script.
Safely tests authentication, model availability, and live inference with Gemma 4.
NEVER HARDCODE OR PRINT TOKENS IN THIS FILE OR TERMINAL.
"""

import os
import sys
import requests
from huggingface_hub import InferenceClient
from huggingface_hub.inference._providers import _fetch_inference_provider_mapping

def main():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
    if not token or not token.strip():
        print("[-] ERROR: HF_TOKEN environment variable is not set.", file=sys.stderr)
        print("[-] Set your token in the current terminal session before running:", file=sys.stderr)
        print("      $env:HF_TOKEN=\"your_huggingface_token_here\"", file=sys.stderr)
        sys.exit(1)

    model_id = os.environ.get("HF_MODEL_ID") or os.environ.get("HUGGINGFACE_MODEL") or "google/gemma-4-26B-A4B"
    provider = os.environ.get("HF_PROVIDER", "auto")

    print("=================================================================")
    print(" SuchnaSetu AI — Hugging Face Gemma 4 Inference Verification")
    print("=================================================================")
    print(f"[*] Target Model ID  : {model_id}")
    print(f"[*] Provider Routing : {provider}")
    print("[*] Checking Hugging Face token authentication...")

    # 1. Verify token with whoami
    try:
        whoami_resp = requests.get(
            "https://huggingface.co/api/whoami-v2",
            headers={"Authorization": f"Bearer {token.strip()}"},
            timeout=10,
        )
        if whoami_resp.status_code == 200:
            user_data = whoami_resp.json()
            username = user_data.get("name", "unknown")
            user_type = user_data.get("type", "user")
            print(f"[+] Authentication SUCCESS: Logged in as '{username}' ({user_type}).")
        elif whoami_resp.status_code in (401, 403):
            print(f"[-] Authentication FAILED: HTTP {whoami_resp.status_code} Unauthorized.", file=sys.stderr)
            print("[-] Please ensure your HF_TOKEN is valid and has read permissions.", file=sys.stderr)
            sys.exit(2)
        else:
            print(f"[!] Warning: whoami-v2 returned HTTP {whoami_resp.status_code}.")
    except Exception as e:
        print(f"[-] Network error verifying token: {e}", file=sys.stderr)
        sys.exit(3)

    # 2. Check provider mapping
    print(f"[*] Querying serverless inference providers for '{model_id}'...")
    try:
        providers = _fetch_inference_provider_mapping(model_id)
        if providers:
            print(f"[+] Found {len(providers)} inference provider(s) for '{model_id}':")
            for p in providers:
                print(f"    - Provider: {p.provider} (status: {p.status}, task: {p.task})")
        else:
            print(f"[!] Note: No auto-router providers listed specifically for '{model_id}'.")
    except Exception as e:
        print(f"[!] Note: Provider mapping check info: {e}")

    # 3. Test chat completion
    print("\n[*] Sending minimal test prompt to Gemma...")
    prompt = (
        "A government scholarship notice states the application deadline is "
        "30 November 2026. Explain the deadline in one simple sentence."
    )

    try:
        client = InferenceClient(
            provider=provider,
            api_key=token.strip(),
            timeout=120,
        )

        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.1,
        )

        reply = response.choices[0].message.content
        print("\n[+] LIVE INFERENCE SUCCESSFUL!")
        print("-----------------------------------------------------------------")
        print(f"Prompt: {prompt}")
        print("-----------------------------------------------------------------")
        print(f"Gemma 4 Response:\n{reply.strip()}")
        print("-----------------------------------------------------------------")
        print("[+] Provider integration is verified and operational.")

    except Exception as e:
        print(f"\n[-] Live inference failed with model '{model_id}':", file=sys.stderr)
        err_type = type(e).__name__
        status = getattr(getattr(e, "response", None), "status_code", None)
        print(f"    Error Type  : {err_type}", file=sys.stderr)
        if status:
            print(f"    HTTP Status : {status}", file=sys.stderr)
        print(f"    Details     : {e}", file=sys.stderr)

        # Suggest alternative models if exact ID is not deployed on free serverless tier
        if model_id != "google/gemma-4-26B-A4B-it":
            print("\n[i] TIP: You can test the instruction-tuned variant with:", file=sys.stderr)
            print("    $env:HF_MODEL_ID=\"google/gemma-4-26B-A4B-it\"", file=sys.stderr)
            print("    .\\.venv\\Scripts\\python.exe test_hf_gemma.py", file=sys.stderr)
        print("[i] Or test Gemma 2:", file=sys.stderr)
        print("    $env:HF_MODEL_ID=\"google/gemma-2-9b-it\"", file=sys.stderr)
        print("    .\\.venv\\Scripts\\python.exe test_hf_gemma.py", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()
