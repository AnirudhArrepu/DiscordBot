import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO


load_dotenv()

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

class NightFury(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents, command_prefix = "!")
        
        # Configure Gemini
        genai.configure(api_key=API_KEY)
        # Configure models
        self.text_model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        
    async def on_ready(self):
        print("UP AND RUNNING {0.user}".format(self))
    
    async def on_message(self, message: discord.Message) -> None:
        
        if message.author == self.user:
            return
        command = message.content
        print(command)
        
        if command.startswith("!analyse"):
            await self.get_website_info(message=message, text=command.split(" ")[1:])
        elif command.startswith("!vision"):
            await self.get_image_info(message=message)
        elif command.startswith("!answer"):
            response=self.text_model.generate_content(command)
            text = response.text
            await message.channel.send(text)
        
    async def get_image_info(self, message):
        if message.attachments:
            imgurl = message.attachments[0]
            
            async with message.channel.typing():
                image_bits = self.download_image(imgurl)
                image = Image.open(BytesIO(image_bits))
                
                response = self.vision_model.generate_content(image)
                text = response.text
                
                prompt = f"""The following text is the response from a Gemini Vision model analyzing an image:

                {text}

                Please reformat this response into a clear and concise summary with the following structure:

                **Image:**

                * Briefly describe the main subject(s) in the image.

                **Details:**

                * Describe any interesting details or objects in the image.

                **Additional Notes:**
                *Include any relevant information not contained.
                """

                response=self.text_model.generate_content(prompt)
                text = response.text
                await message.channel.send(text)
            
    @staticmethod
    def download_image(imgurl):
        respone = requests.get(url=imgurl)
        
        if respone.status_code == 200:
            return respone.content
        else:
            print("error")
        
        
    async def get_website_info(self, message: discord.Message, text) -> None:
        prompt = prompt = f"""Analyze the website: {text}

        **Here's what I'm looking for:**
        
        * **Purpose:** What is the main function or service offered by the website? Is it an e-commerce store, a news website, a portfolio, a blog, etc.?
        * **Content:** Briefly describe the type of content found on the website (e.g., articles, products, services, images, videos).
        * **Target Audience:** Who is the website aimed at? (e.g., businesses, general consumers, a specific niche)
        
        **Pay close attention to the website's metadata, including the title tag, meta description, and keywords.** This information can provide valuable clues about the website's purpose and target audience.
        
        **Keep the response concise and informative.**"""

        async with message.channel.typing():
            response = self.text_model.generate_content(prompt)
            text = response.text
            await message.channel.send(text)

def start_bot():
    nf = NightFury()
    nf.run(token=TOKEN)
    
if __name__ == "__main__":
    start_bot()