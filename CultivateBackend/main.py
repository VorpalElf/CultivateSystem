import os
from flask import Flask, request
from google import genai
from google.genai.types import GenerateContentConfig
import serpapi
import json
import requests

# Load API key
gemini_key = os.environ.get("GEMINI_API_KEY")
serp_key = os.environ.get("SERP_API_KEY")
client = genai.Client(api_key=gemini_key)

app = Flask(__name__)

# Server request route
@app.route('/server-request', methods=['POST'])
def handle_post():
    # Check API Key
    if gemini_key == None:
        return {'response': 'No Gemini Key'}, 200
    if serp_key == None:
        return {'response': 'No SERP Key'}, 200
    
    # Handle data
    data = request.get_json()
    user_input = data.get("input", "")
    history = data.get("history", "")
    
    # Send request to Gemini and save it
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input,
        config=GenerateContentConfig(
            system_instruction=(
                "You are an API that returns answers in a JSON format only."
                "If the user is asking to find, search for, or generate leads/clients/contacts/businesses/organizations, respond with JSON: {\"intent\": \"lead\"}\n"
                "Otherwise, return {\"intent\": \"irrelevant\"}"
                "Do not include any text outside the JSON object. The output should be just JSON, no other outputs and no next line\n"
                f"User request: \"{user_input}\""
                f"Conversation history: \"{history}\""
            )
        )
    )
    
    # Handle response and find the query
    response_text = response.text
    start_ind = response_text.find("{")
    end_ind = response_text.rfind("}") +1
    response_text = response_text[start_ind:end_ind]
    response_json = json.loads(response_text)
    
    if response_json["intent"] == "irrelevant":
        print("Irrelevant")
        irrelevant = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input)
        
        irrelevant_text = irrelevant.text
        return {'response': irrelevant_text}, 200
    
    # Extract value with string
    print("Relevant")
    direct_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_input,
        config=GenerateContentConfig(
            system_instruction="You are a helpful assistant. Generate a query so the user can find the appropritate client. Only output the query"
            )
        )
    
    search_query = direct_response.text
    print(f"Query: {search_query}")
    
    # SERP API Queries
    serp_url = "https://serpapi.com/search.json"
    params = {"q": search_query, "api_key": serp_key, "num": 10}
    serp_response = requests.get(serp_url, params=params)
    serp_data = serp_response.json()
    results = serp_data.get("organic_results", [])[:10]
    print("Querying")
    
    # Send Results to Gemini for analysis
    final_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="You are an assistant that analyzes search results and provides concise, helpful answers with a brief explanation. Do not include a 'sources' field or list all URLs.",
        config=GenerateContentConfig(
            system_instruction=(
                f"User question: {user_input}\n"
                f"Here are the top 10 Google search results in JSON format: {results}\n"
                "Based on these results, provide:\n"
                "1. Provide 5 possible options of leads/companies. What is the email of each commany or lead. If you cannot find the email in the results, please search the companies or leads' website.\n"
                "2. A brief explanation of how and why you drew your conclusion.\n" 
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