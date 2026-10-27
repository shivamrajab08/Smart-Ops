# Smart Ops 🚀
Automated Deployment and Monitoring Platform using DevOps.

## Live Demo
- Frontend: https://smart-ops-dashboard-six.vercel.app
- Backend: https://smart-ops-b0dj.onrender.com
- Health Check: https://smart-ops-b0dj.onrender.com/health
- GitHub: https://github.com/shivamrajab08/Smart-Ops
- Docker Hub: https://hub.docker.com/r/xrg1114/smart-ops

## Features
- Interactive dashboard
- Application health monitoring
- External software & API testing (live HTTP probes, latency tracking, status code verification)
- GitHub commit history
- Automated tests using pytest
- CI/CD with GitHub Actions
- Docker image publishing
- Backend on Render and frontend on Vercel

## Technologies
Python, Flask, HTML, CSS, JavaScript, Docker, GitHub Actions, Render, Vercel, pytest.

## Run Locally
1. Clone the repository:
   `git clone https://github.com/shivamrajab08/Smart-Ops.git`
2. Open the project folder.
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the application:
   `python app.py`
5. Open `http://127.0.0.1:5000`.

## Run Tests
`python -m pytest -v`

## Docker
Pull the image:
`docker pull xrg1114/smart-ops:latest`

Run it:
`docker run -p 5000:5000 xrg1114/smart-ops:latest`

## API Endpoints
- `/` — Dashboard
- `/health` — Health check
- `/api/status` — Application status
- `/api/deployments` — GitHub commit history
- `/api/test-service` — Test external software/API health and latency (POST)

## Author
Ratnakar Gupta — B.Tech Computer Science and Engineering

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and test them locally.
4. Commit and push your changes to your fork.
5. Open a Pull Request against the original repository.

Please ensure your changes are tested before submitting a Pull Request.

## Development

- Install dependencies using `pip install -r requirements.txt`.
- Run the application using `python app.py`.
- Run automated tests using `python -m pytest -v`.

