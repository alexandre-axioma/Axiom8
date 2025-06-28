import requests
import json

def test_invoke_agent():
    """
    Tests the /invoke endpoint of the agent API with a sample query.
    """
    url = "http://127.0.0.1:8000/api/v1/invoke"
    payload = {
        "query": "I need a workflow that triggers on a new tweet with the hashtag #n8n, then translates the tweet to English, and finally posts it to a Slack channel."
    }
    headers = {
        'Content-Type': 'application/json'
    }

    print(f"Sending request to {url} with payload:")
    print(json.dumps(payload, indent=2))

    try:
        with requests.post(url, json=payload, headers=headers, stream=False) as response:
            response.raise_for_status()  # Raise an exception for bad status codes
            
            print("\n--- Agent Response ---")
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            print("--- End of Response ---")

    except requests.exceptions.RequestException as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    test_invoke_agent()
