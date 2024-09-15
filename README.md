# cs24-p2-TEAM DEADBEEF
Hello! </br>
This is the repo for phase 2 of Code Samurai 2024 presented by Team DEADBEEF

Team members: </br>
#1 Md. Abu Bakor Siddique (abubakor@iut-dhaka.edu) </br>
#2 Shahrin Hossain (shahrin@iut-dhaka.edu) </br>
#3 Fateen Noor Rafee (fateennoor@gmail.com)

This project was prepared to run on windows

#### default login creds:
email: admin@amin.com
password: 123456789


Only README, DOCKERFILE and requirements.txt were added in the latest commit

# EcoSync - Efficient Waste Management System

EcoSync is a web-based platform designed for efficient waste management in Dhaka North City. This project was developed as part of **Team Deadbeef's** entry for **Code Samurai 2024**. The platform allows various users, such as **STS Managers**, **Landfill Managers**, and **Admins**, to manage and optimize waste collection and disposal operations. 

While this was our first full-stack web project, built with **vanilla JavaScript**, **HTML**, **CSS** for the frontend, and **Flask** with **Python** and **SQLite** for the backend, we are proud of its functionality and the potential for real-world applications.

[Watch the video](https://drive.google.com/drive/folders/141-0vB3OQ5ShdH675NqJokn20TJd9DqM)


## Features

- **User Authentication**: Users can log in and verify their email accounts.
- **Admin Role**: The admin can create, assign, and edit roles, permissions, and users in the system.
- **STS Manager**: The STS Manager has control over specific STS (Secondary Transfer Station) locations. They can view, add, and manage STS records.
- **Landfill Manager**: The Landfill Manager can manage landfill locations and records, and optimize routes for waste disposal.
- **Role & Permission Management**: Admins can assign permissions to users based on their role.
- **Fleet Optimization**: Efficient routing for trucks to minimize travel time and maximize productivity.
- **Waste Tracking**: View and manage the status of waste collection at various locations.

## System Roles

The website has 3 key user roles, each with specific functionalities:

1. **Admin**: 
   - Assign and manage user roles.
   - Add, edit, or delete STS and landfill sites.
   - Modify permissions for other users.
   
2. **STS Manager**:
   - Add or view records at STS sites.
   - Optimize waste transport routes from STS sites.

3. **Landfill Manager**:
   - Add or view landfill records.
   - Oversee waste management at landfill sites.

## Tech Stack

- **Frontend**: 
  - Vanilla **HTML**, **CSS**, and **JavaScript**
  - Basic styling and layout for user-friendly interfaces.

- **Backend**: 
  - **Flask** (Python web framework)
  - **SQLite** (Database for storing user data, site records, and roles)

## Install the required dependencies and run:
```bash
pip install -r requirements.txt
python app.py
http://localhost:5000
```
