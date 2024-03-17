from openai import OpenAI 

import base64
import requests
import os

from flask import Flask, request, session, jsonify

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

#----------------------------------------------------------------------------------------------------
system_setup = "You're an AI assistant at TopDoctors. When you're asked to write a text, a paragraph or an article reply with an article of around 700 words."

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file_img(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG

#----------------------------------------------------------------------------------------------------
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

#----------------------------------------------------------------------------------------------------
def chatbot_text(prompt):
    if 'messages' not in session:
        session['messages'] = [{"role": "system", "content": system_setup},]

    if 'conversation_cost' not in session:
        session['conversation_cost'] = 0.0
  
    if 'total_prompts_cost' not in session:
        session['total_prompts_cost'] = 0.0

    if 'total_responses_cost' not in session:
        session['total_responses_cost'] = 0.0

    # Add each new message to the list
    session["messages"] = session["messages"] + [{"role": "user", "content": prompt}]

    completion = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = session["messages"])
  
    # Getting the generated response
    chat_message = completion.choices[0].message.content

    # Getting the number of consumed tokens in this prompt
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens

    session['total_responses_cost'] += completion_tokens * 0.0015
    session['total_prompts_cost'] += prompt_tokens * 0.0005
    total_conversation_cost = session['total_responses_cost'] + session['total_prompts_cost']

    # Adding the response to the messages list
    session["messages"] = session["messages"] + [{"role": "assistant", "content": chat_message}]

    print("\nHere you have the session:\n\n", session["messages"])

    returned_dict = {
        "1-Chat response": chat_message,
        "2-Current_prompt_tokens": prompt_tokens,
        "3-Current_completion tokens": completion_tokens,
        "4-Total_prompts_cost": str(session['total_prompts_cost'])+"$",
        "5-Total_responses_cost" : str(session['total_responses_cost'])+"$",
        "6-All_conversation_cost": str(total_conversation_cost)+"$",
    }

    return returned_dict


#----------------------------------------------------------------------------------------------------
def chatbot_image(images_path_list, prompt):

    content_list = [{
            "type": "text",
            "text": prompt 
            },]
    #we can directly make a for loop to the files folder
    for image_path in images_path_list:
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
        "role": "system",
        "content": system_setup,
        },
        {
        "role": "user",
        "content": content_list,
        }
    ],
    "max_tokens": 1000
    }

    completion = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(completion)

    return completion.json()["choices"][0]["message"]["content"]


#----------------------------------------------------------------------------------------------------
@app.route('/get_response', methods=['POST'])
def get_response():
    prompt = request.form['prompt']

    files = request.files.getlist('file')
    print(files)
    # check if the post request has the file part
    if not files :
        generated_response = chatbot_text(prompt)
        
    else:
        images_path_list = []
        for index, file in enumerate(files):
            
            if allowed_file_img(file.filename):
                image_name="image"+str(index)+".jpg"
                image_path=os.path.join("files", image_name)
                #Saving file to project directory
                file.save(image_path)

                images_path_list.append(image_path)

            # Later, we add here other type of file (like excel, .csv, .txt...)

        generated_response = chatbot_image(images_path_list, prompt)


    return jsonify(generated_response), 201
    
#------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)