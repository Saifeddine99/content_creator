from openai import OpenAI 

import base64
import requests
import os

from flask import Flask, request, session, jsonify

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

OPENAI_API_KEY = "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"

model_engine = "gpt-3.5-turbo"
client = OpenAI(api_key=OPENAI_API_KEY)

#----------------------------------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#----------------------------------------------------------------------------------------------------
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#----------------------------------------------------------------------------------------------------
def chatbot_text(prompt):
    system_setup = "You're an AI assistant at TopDoctors. When you're asked to write a text, a paragraph or an article reply with an article of around 700 words."
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": system_setup},]

    # Add each new message to the list
    session["messages"] = session["messages"] + [{"role": "user", "content": prompt}]

    completion = client.chat.completions.create(
    model = model_engine,
    messages = session["messages"])
  
    # Getting the generated response
    chat_message = completion.choices[0].message.content

    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    total_tokens = completion.usage.total_tokens

    # Adding the response to the messages list
    session["messages"] = session["messages"] + [{"role": "assistant", "content": chat_message}]

    print("\nHere you have the session:\n\n", session["messages"])

    returned_dict = {
        "prompt_tokens": prompt_tokens,
        "completion tokens": completion_tokens,
        "Total tokens": total_tokens,
        "chat response": chat_message,
    }

    return returned_dict


#----------------------------------------------------------------------------------------------------
def chatbot_image(paths_list, prompt):

    content_list = [{
            "type": "text",
            "text": """you are a content creator of a company called top doctors, I aim you to produce texts on polite english, the style must be periodistic...\n
                        """ + prompt
            },]
    #we can directly make a for loop to the files folder
    for image_path in paths_list:
        # Getting the base64 string
        base64_image = encode_image(image_path)
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            })

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": content_list,
        }
    ],
    "max_tokens": 300
    }

    completion = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return(completion.json()["choices"][0]["message"]["content"])


#----------------------------------------------------------------------------------------------------
@app.route('/get_response', methods=['POST'])
def get_response():
    prompt = request.form['prompt']

    files = request.files.getlist('file')
    # check if the post request has the file part
    if not files :
        generated_response = chatbot_text(prompt)
        
    else:
        paths_list = []
        for index, file in enumerate(files):
            
            if allowed_file(file.filename):
                image_name="image"+str(index)+".jpg"
                image_path=os.path.join("files", image_name)
                #Saving file to project env
                file.save(image_path)

                paths_list.append(image_path)

        generated_response = chatbot_image(paths_list, prompt)

    return jsonify(generated_response), 201
    
#------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)