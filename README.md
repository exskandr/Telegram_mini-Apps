The program is created for a test task and has an educational purpose. The program is a mini-application for a Telegram bot. The mini-application is based on the Flask framework.

With the help of the bot, you can select a photo, and the connected OpenAI API will generate a description for this image.

To run the application, you need:

Docker;
NGROK;
BOT_TOKEN (create a Telegram bot using https://t.me/botfathermeb and get the token there)
OPENAI_API_KEY - OpenAI token
WEBAPP_URL - link to the mini web application's page. If you use NGROK, it should be the HTTPS link provided by NGROK.
Also, don't forget to create a .env file where you specify BOT_TOKEN, OPENAI_API_KEY, and WEBAPP_URL.

Start NGROK by entering the command "ngrok http http://localhost:5000".

Start Docker by entering the command "docker-compose up --build -d".

Go to your bot and test it.
