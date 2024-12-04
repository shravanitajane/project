import streamlit as st
import time       
from streamlit_option_menu import option_menu 
from openai import OpenAI
import requests
import os
import time
from PIL import Image, ImageDraw, ImageFont
import io
import hashlib  
import sqlite3 


conn = sqlite3.connect('data.db')
c = conn.cursor()


OPENAI_API_KEY = "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"

avatarlist = {
    "Male": "https://www.thesun.co.uk/wp-content/uploads/2021/10/2394f46a-c64f-4019-80bd-445dacda2880.jpg?w=670",
    "Female": "https://cubedautomation.com/assets/mayuri.jpg"
}



def generate_video(prompt, avatar_url, gender):
    url = "https://api.d-id.com/talks"
    headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "Authorization" : "Basic dmlzaGFsbWF0ZTEwQGdtYWlsLmNvbQ:k-c5YK5EJIV32Qcl4nhpQ"
}
    if gender == "Female":
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-JennyNeural"
                },
                "ssml": "false",
                "input":prompt
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0"
            },
            "source_url": avatar_url
        }

    if gender == "Male":
        payload = {
            "script": {
                "type": "text",
                "subtitles": "false",
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-BrandonNeural"
                },
                "ssml": "false",
                "input":prompt
            },
            "config": {
                "fluent": "false",
                "pad_audio": "0.0",
                "driver_expressions": {
                    "expressions": [
                        {
                        "start_frame": 0,
                        "expression": "surprise",
                        "intensity": 1
                        }
                    ]
                    }
            },
            "source_url": avatar_url
        }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(response.text)
            res = response.json()
            id = res["id"]
            status = "created"
            while status == "created":
                getresponse =  requests.get(f"{url}/{id}", headers=headers)
                print(getresponse)
                if getresponse.status_code == 200:
                    status = res["status"]
                    res = getresponse.json()
                    print(res)
                    if res["status"] == "done":
                        video_url =  res["result_url"]
                    else:
                        time.sleep(10)
                else:
                    status = "error"
                    video_url = "error"
        else:
            video_url = "error"   
    except Exception as e:
        print(e)      
        video_url = "error"      
        
    return video_url

     
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password,hashed_text): 
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


def create_usertable():     
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data

def view_all_users():            
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


def main():
    st.header("BrandBuddy: AI Powered Marketing Friend")
    with st.sidebar:
        choice = option_menu("Menu", ["Home", 'Signup', 'Login', 'Setting'], 
        icons=['house', 'box-arrow-right','person-plus-fill', 'gear'], default_index=0)
    if choice == "Home":
        st.markdown('<div style="text-align: justify;">BrandBuddy is a revolutionary AI-powered marketing companion that leverages the OpenAI API to transform the landscape of digital marketing. Through advanced algorithms and machine learning capabilities, BrandBuddy can generate engaging content, captivating images, and even AI talking avatars. This innovative approach not only saves time and resources but also ensures consistent quality and creativity across various marketing campaigns.</div>', unsafe_allow_html=True)
        st.image("Arch.png")
        st.markdown('<div style="text-align: justify;">By integrating the OpenAI API into BrandBuddy, marketers can access a wealth of tools and functionalities to enhance their strategies. From crafting compelling social media posts to creating personalized customer experiences with AI avatars, BrandBuddy streamlines the marketing process and helps businesses stay ahead in today\'s competitive market.With its intelligent features and user-friendly interface, BrandBuddy emerges as a trusted ally for marketers, enabling them to reach their target audience effectively and drive meaningful engagement.</div>', unsafe_allow_html=True)
            
    elif choice == "Login":
        st.sidebar.subheader("Please Enter Valid Credentials")
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login/Logout"):
            create_usertable()
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))
            if result and username != '' and password != '':
                st.sidebar.success("login Success.")
                selected2 = option_menu(None, ["Content", "Image", "AI Avatar"], 
                icons=['blockquote-left', 'file-earmark-image', "person-video"], 
                menu_icon="cast", default_index=0, orientation="horizontal")
                if selected2 == 'Content':
                    st.subheader("Generate Content")
                    user_input = st.text_input("Enter your message:")
                    if st.button("Generate Response"):
                        client = OpenAI(api_key=OPENAI_API_KEY)
                        response = client.chat.completions.create(
                            model='gpt-3.5-turbo',
                            messages=[
                                {'role': 'user', 'content': user_input}
                            ]
                        )

                        st.text("AI Response:")
                        st.write(response.choices[0].message.content, style={"text-align": "justify"})
                elif selected2 == 'Image':
                    st.subheader("Social Media Post Generator")
                    client = OpenAI(api_key=OPENAI_API_KEY)
                    prompt = st.text_area("Enter the prompt for image generation", "A photorealistic image of a ginger cat curled up on a windowsill, gazing out at a bustling city street slick with rain.")
                    if st.button("Generate Image"):
                        response = client.images.generate(
                            model='dall-e-3',
                            prompt=prompt,
                            style='vivid',
                            size='1024x1024',
                            quality='standard',
                            n=1
                        )
                        image_url = response.data[0].url
                        st.image(image_url, caption="Generated Image", use_column_width=True)


                
                elif selected2 == 'AI Avatar':
                    st.subheader("Generate Avatar Video")
                    prompt = st.text_area("Enter Text Prompt", "Once upon a time...")
                    avatar_options = ["Male", "Female"]
                    avatar_selection = st.selectbox("Choose Avatar", avatar_options)
                    avatar_url = avatarlist[avatar_selection]
                    if st.button("Generate Video"):
                        st.text("Generating video...")
                        try:
                            video_url = generate_video(prompt, avatar_url, avatar_selection) 
                            if video_url!= "error":
                                st.text("Video generated!")
                                st.subheader("Generated Video")
                                st.video(video_url) 
                            else:
                                st.text("Sorry... Try again")
                        except Exception as e:
                            print(e)
                            st.text("Sorry... Try again", e)
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Signup":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')

        if st.button("Signup"):
            if new_user !='' and new_password != '':
                create_usertable()
                add_userdata(new_user,make_hashes(new_password))
                st.success("You have successfully created a valid Account")
                st.info("Go to Login Menu to login")
            else:
                st.warning("Please Enter valid username and password...")
    
    elif choice == "Setting":
        st.subheader("Set OpenAI API Keys and Credentials")
        key = st.text_input("API Key")
        secrete = st.text_input("Secrete",type='password')
        st.button("Save")


if __name__ == '__main__':
	main()