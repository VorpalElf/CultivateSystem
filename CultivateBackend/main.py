import os
from flask import Flask, request
from google import genai
from google.genai.types import GenerateContentConfig
from serpapi import GoogleSearch
import json

# Load API key
gemini_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key)

app = Flask(__name__)

# Server request route
@app.route('/server-request', methods=['POST'])
def handle_post():
    # Handle data
    data = request.get_json()
    user_input = data.get("input", "")
    
    # Send request to Gemini and save it
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input,
        config=GenerateContentConfig(
            system_instruction=(
                # Change to "based on lead"
                "You are an API that returns answers in a JSON format suitable for the SERP API. "
                "If the user is asking to find, search for, or generate leads/clients/contacts/businesses/organizations, generate a Google search query string in a JSON object with a 'query' field.\n"
                "Otherwise, return False"
                "Example: {\"query\": \"What is the capital of France?\"}. "
                "Do not include any text outside the JSON object. The output should be just JSON, no other outputs and no next line\n"
                f"User request: \"{user_input}\""
            )
        )
    )
    
    # Handle response and return
    response_text = response.text
    
    if response_text == "False":
        print("Irrelevant")
        response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input)
        
        return {'response': response}, 200
    
    # Extract value with string
    end = len(response_text)
    query = response_text[9:end]
    print(query)
    
    
    # SERP API Queries
    serp_key = os.environ.get("SERP_API_KEY")
    params = {
        "engine": "Google",
        "q": str(query),
        "api_key": serp_key
    }
    search = GoogleSearch(params)
    if "organic_results" in search.get_dict():
        results = search.get_dict()["organic_results"]
        results_json = json.dumps(results)
    else:
        print("No organic results")
        results = []
    
    # Send Results to Gemini for analysis
    final_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"This is the user's requirements and queries: {user_input}\n and here are the top 10 results based on their queries {results_json}\n"
        "Please analyse these results and gives the best company or client that suits the user's requirements.",
        config=GenerateContentConfig(
            system_instruction=(
                #TODO Change to "based on lead"
                "You're an assistant to find the best company (or leads) that suits the user's requirements", 
                "You must provide a brief explanation of why choosing the company, as well as compared with other companies"
            )
        )
    )
    
    # Return response answer
    try:
        answer = final_response.text
    except AttributeError:
        answer = str(final_response)
    
    return {'response': answer}, 200

if __name__ == '__main__':
    app.run(host='192.168.1.143', port=5000, debug=True)