import requests
import concurrent.futures

WALLET_ID = "476bcc4b-7129-4bea-9c0b-4f6a106261ec"
URL = f"http://127.0.0.1:8000/wallet/{WALLET_ID}/debit"

def make_request():
    try:
        response = requests.post(URL, json={"amount": 10})
        return response.status_code
    except Exception as e:
        print("Request error:", e)
        return None

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(50)]
        results = [f.result() for f in futures]

    print("All status codes:", results)
    print("Success:", results.count(200))
    print("Failed (400):", results.count(400))
    print("Other errors:", len(results) - results.count(200) - results.count(400))