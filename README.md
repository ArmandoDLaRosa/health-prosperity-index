
# Health and Prosperity Index

## Project Overview
Hey! This project is all about calculating and showing off a health and prosperity index for US states. We’re pulling data from the DataUSA API and using it to give you some cool stats. You’ll get to see how healthy and prosperous each state is, all wrapped up in a neat little package.

## Setup Instructions
Alright, let’s get you set up.

1. **Clone the Repo**:
   - First, grab the code:
     ```bash
     git clone https://github.com/YOUR-USERNAME/health-prosperity-index.git
     cd health-prosperity-index
     ```

2. **Build the Docker Image**:
   - Let’s build this thing. Just run:
     ```bash
     docker build -t health-prosperity-app .
     ```

3. **Run the Docker Container**:
   - Now, spin up the container with:
     ```bash
     docker run -d -p 8501:8501 health-prosperity-app
     ```
   - After that, open your browser and head over to [http://localhost:8501](http://localhost:8501). You’ll see the index data and logs there. Cool, right?

## Usage
So, what does this project do? It calculates an index that tells you how healthy and prosperous different US states are. This is based on some variables like life expectancy, income, education level, and unemployment rate. All this info is fetched from the DataUSA API and saved in a MySQL database.

## Testing
If you want to make sure everything’s working (which you probably should), here’s how you can test it:

1. **Run Tests**:
   - You can run the tests like this:
     ```bash
     pytest tests/
     ```

2. **Check Coverage**:
   - Wanna see how much of the code is covered by tests? Run:
     ```bash
     coverage run -m pytest tests/
     coverage report
     ```

## Error Handling
Yeah, sometimes stuff breaks. If the cron job messes up, it’ll log the error and even send you an email to let you know something went wrong. Just make sure you’ve set up your Gmail account correctly with an app password.

## Local Development
Wanna mess around with the code on your own machine? No problem. Just use the `development` environment in the `config.json` file. Run the `init_db.py` script to set up your local database, and you’re good to go.

## Performance Improvement Tools
I used some tools like `pytest` for testing and `coverage` for making sure we didn’t miss anything important. Also, `smtplib` helps with sending email alerts when something goes wrong. Handy, right?
