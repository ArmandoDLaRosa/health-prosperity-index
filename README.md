# Health and Prosperity Index

## Project Overview
Hey! This project is all about calculating and showing off a health and prosperity index for the entire US. We’re pulling data from the DataUSA API and using it to give you some cool stats. You’ll get to see how healthy and prosperous the country is, all wrapped up in a neat little package.

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
     docker build -t health-prosperity-index-app .
     ```

3. **Run the Docker Container**:
   - Now, spin up the container with:
     ```bash
     docker run -d -p 8501:8501 -p 3307:3306 health-prosperity-index-app
     ```
   - After that, open your browser and head over to [http://localhost:8501](http://localhost:8501). You’ll see the index data and logs there. Cool, right?

## Usage
So, what does this project do? It calculates an index that tells you how healthy and prosperous the US is as a whole. This is based on variables like population, household income, education level, and home ownership rate. All this info is fetched from the DataUSA API and saved in a MySQL database.

## Database Initialization
When you first run the app, the Docker container automatically sets up the MySQL database for you. If the database or user doesn’t exist, it creates them, so you don’t have to worry about setting it up manually. Sweet, right?

## Cron Jobs
There’s a cron job running every 5 minutes to fetch the latest data and update the index. The cron job also logs its status into the database, so you can keep track of what’s happening.

## Local Development
Wanna mess around with the code on your own machine? No problem. Just use the `development` environment in the `config.json` file. Run the `init_db.py` script to set up your local database, and you’re good to go.

## Testing
To ensure that everything is working, follow these updated steps to run the tests from the project root using `unittest`:

1. **Run Tests**:
   - You can run the tests from the project root like this:
     ```bash
     python -m unittest discover -s tests
     ```

2. **Check Coverage**:
   - If you want to check how much of the code is covered by tests, run the following commands from the project root:
     ```bash
     coverage run -m unittest discover -s tests
     coverage report
     ```

Make sure to run these commands from the root directory of your project to ensure the proper paths are used during test discovery and coverage analysis.

## Performance Considerations
To keep things running smoothly, the app also handles database migrations automatically with Alembic. So when the app starts, it’ll make sure your database schema is up to date. No more manual updates needed!

## Conclusion
And that’s it! You’re all set to explore the health and prosperity of the entire US. Enjoy the insights, and feel free to tweak things to suit your needs. Happy coding!