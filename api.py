from flask import Flask, request, render_template, jsonify
import numpy as np
import replicate
import os
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
import pickle as pkl
import psycopg2
from sqlalchemy import create_engine
from datetime import datetime


app = Flask(__name__)


os.environ['REPLICATE_API_TOKEN'] = "r8_3Cn377wOsZ8ywqtFyCCicG5JwHqpHYS0sONIW"
engine = create_engine('postgresql://database230912_user:hd6AsAinYSbQTg9wMX9UCRZJPMbMUUNg@dpg-ck06hrvhdsdc73dbccg0-a.frankfurt-postgres.render.com/database230912')

@app.route("/", methods=["GET","POST"])
def bad_language():
    def error():
        return "DATA ERROR"
        
    if request.method == "POST":

        text = request.form.get('texto', None)
        if text is None:
            return error()
        
        prompt_input = request.args.get('prompt_input', default = "", type = str)
        string_dialogue = "You are a profanity detector assistant. Your answer will be binary. Your task is to analyze an input text and identify any offensive language or words. If you detect offensive language, respond with 'YES.' If you do not detect offensive language, respond with 'NO."
        output = replicate.run('meta/llama-2-70b-chat:35042c9a33ac8fd5e29e27fb3197f33aa483f72c2ce3b0b9d201155c7fd2a287',
                                input={"prompt": prompt_input,
                                  "system_prompt":string_dialogue})
        response = ''.join(output)

        time = str(datetime.now())

        cols = {
            
            'text': prompt_input,
            'prediction': response,
            'time': time
            }
        index = [int(datetime.now().timestamp())]
        
        df = pd.DataFrame(cols, index= index)
        df.to_sql(name="predictions",if_exists='append',con=engine, index = False)
        return render_template('index.html',output = response)
    return render_template('index.html', output = '')
    
@app.route('/get_logs', methods=["GET"])
def get_logs():
    return jsonify(pd.read_sql_query("select * from predictions", con = engine).to_dict("records"))

@app.route("/images_generator", methods=["GET","POST"])
def images_generator():

    if request.method == "POST":

        peticion_imagen = request.form.get('prompt', None)
        output = replicate.run("stability-ai/sdxl:8beff3369e81422112d93b89ca01426147de542cd4684c244b673b105188fe5f",
                                 input= {"prompt": peticion_imagen})
    
        return render_template('pic_gen.html', output = output )
    return render_template('pic_gen.html', output = 'Escribe un texto para crear una imagen')


if __name__=="__main__":
    app.run(debug=True, port=8000)


# import streamlit as st
# import replicate
# import os
# replicate_api = 'r8_5x6EJXbsnYzL9aERZqTOhMbYQpKP2QO0o4C9e'
# os.environ['REPLICATE_API_TOKEN'] = replicate_api
# def generate_llama2_response(prompt_input):
#     string_dialogue = "Tu función principal como analizador de lenguaje inapropiado es examinar un texto y determinar si contiene palabras o expresiones ofensivas. Si detectas lenguaje inapropiado, tu respuesta debe ser 'SÍ'. Si no detectas lenguaje inapropiado, tu respuesta debe ser 'NO'."
#     output = replicate.run('meta/llama-2-70b-chat:35042c9a33ac8fd5e29e27fb3197f33aa483f72c2ce3b0b9d201155c7fd2a287',
#                            input={"prompt": prompt_input,
#                                   "system_prompt":string_dialogue})
#     return output


# prompt_input = ""

# response = generate_llama2_response(prompt_input)
# full_response = ''
# placeholder = st.empty()

# for item in response:
#     full_response += item
#     placeholder.markdown(full_response)
# placeholder.markdown(full_response)
# message = {"role": "Assistant", "content": full_response}


# print(message['content'])