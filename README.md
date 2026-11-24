# Exercise Analyzer

A Flask web app that grades your gym-exercise form from a video. Upload a clip, pick the exercise, and the app:

1. tracks your body pose frame by frame with **MediaPipe Pose**,
2. computes joint angles (elbow, shoulder or knee),
3. finds every repetition and checks its range of motion,
4. gives you a **mark from 10**,
5. writes short feedback with **GPT-4o** (through GitHub Models).

Each result is saved to your account so you can follow your progress on charts.

## Supported exercises

| Exercise | Joint angle measured | A rep counts as correct when |
|---|---|---|
| Bicep curl | Elbow (shoulder–elbow–wrist) | arm opens to ≥ 160° and closes to ≤ 65° |
| Tricep extension | Elbow (shoulder–elbow–wrist) | arm opens to ≥ 165° and closes to ≤ 90° |
| Lateral raise | Shoulder (elbow–shoulder–hip) | arm rises to ≥ 80° and lowers to ≤ 30° |
| Shoulder press | Shoulder (elbow–shoulder–hip) | arm rises to ≥ 80° and lowers to ≤ 30° |
| Leg press | Knee (hip–knee–ankle) | leg opens to ≥ 160° and bends to ≤ 90° |

## How the grading works

```
video ──► MediaPipe Pose ──► 33 landmarks / frame ──► joint angle / frame
                                                         │
                                Savitzky–Golay smoothing (window 20, order 2)
                                                         │
                         peaks = top of each rep, valleys = bottom of each rep
                                                         │
                       each peak / valley outside the threshold = 1 mistake
                                                         │
                       mark = 10 − 5 × mistakes / number of reps
                                                         │
                            angles + mark ──► GPT-4o ──► feedback text
```

- **Left and right sides are graded separately** and then combined.
- **Visibility check:** if the elbow (or the knee, for leg press) drops below 50% MediaPipe visibility in any frame, that side is left out of the grade. If neither side is visible, the mark is 0.
- Angles are measured in 2D, in the image plane. For accurate results, film so that the movement happens roughly parallel to the camera, and keep the whole limb in frame for the full set.

## Tech stack

- **Backend:** Flask, Flask-Login, Flask-SQLAlchemy (SQLite), Werkzeug password hashing (PBKDF2-SHA256)
- **Computer vision:** MediaPipe Pose, OpenCV
- **Signal processing:** NumPy, SciPy (`savgol_filter`, `find_peaks`)
- **AI feedback:** OpenAI Python SDK → GitHub Models (`openai/gpt-4o`)
- **Frontend:** HTML/CSS, vanilla JavaScript, Chart.js (loaded from CDN)

## Project structure

```
exercise-analyzer/
├── hello.py              # Flask app: routes, auth, database models
├── AnalyzerClass.py      # ExerciseAnalyzer: angles, rep detection, grading, LLM feedback
├── BodyModule.py         # PostureDetector: wrapper around MediaPipe Pose
├── templates/            # index, login, register, upload, results, chart, change-username, change-password
├── static/
│   ├── css/              # one stylesheet per page
│   ├── js/               # form submission (fetch), results page, progress charts
│   └── images/logo.png
├── instance/             # SQLite database (created automatically)
└── tempCodeRunnerFile.py # leftover file from VS Code Code Runner (older copy of hello.py)
```

## Getting started

### Requirements

- **Python 3.10–3.12.** The code uses `match` (needs 3.10+). It uses MediaPipe's legacy `mp.solutions` API, which is not present in recent MediaPipe releases (checked: 0.10.30+). MediaPipe 0.10.21 has it, and its wheels do not install on Python 3.13.
- A **GitHub token** with access to GitHub Models (for the AI feedback).
- A desktop environment: during analysis the app opens an OpenCV preview window (`cv2.imshow`).

### Install and run

```bash
git clone https://github.com/andreibucur1/exercise-analyzer.git
cd exercise-analyzer

python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate

pip install "mediapipe==0.10.21" opencv-python flask flask-sqlalchemy flask-login numpy scipy matplotlib openai

mkdir uploads                        # uploaded videos are saved here temporarily

export GITHUB_TOKEN=your_token_here  # Windows PowerShell: $env:GITHUB_TOKEN="your_token_here"

python hello.py
```

Open **http://127.0.0.1:5000**, create an account, then go to **Upload**.

The SQLite database is created automatically at `instance/users111.db`.

## Usage

1. **Register** or **log in**.
2. Go to **Upload**, pick a video file and choose the exercise.
3. Wait for the analysis. You'll be sent to **Results**, which shows your mark and the AI feedback.
4. Open **Chart** to see your marks over time, with one chart per exercise.
5. You can change your username or password from your account pages.

The video is deleted from `uploads/` right after it is analyzed.

## Routes

| Route | Method | Login required | Purpose |
|---|---|---|---|
| `/` | GET | no | Home page |
| `/register` | GET, POST | no | Create an account (password ≥ 6 characters) |
| `/login` | GET, POST | no | Log in |
| `/logout` | GET | no | Log out |
| `/change-username` | GET, POST | yes | Change username |
| `/change-password` | GET, POST | yes | Change password |
| `/upload` | GET | yes | Upload page |
| `/analyze` | POST | yes | Analyze a video (`video` file + `exercise` field) → `{success, mark, message}` |
| `/results` | GET | yes | Results page |
| `/api/exercise-data` | GET, POST | yes | The current user's history → `{results: [{exercise, mark, timestamp}]}` |
| `/chart` | GET | yes | Progress charts |

`exercise` values: `bicepCurl`, `tricepExtension`, `lateralRaise`, `shoulderPress`, `legPress`.

## Data model

- **users**: `id`, `username` (unique), `email`, `password` (hashed)
- **exercise_data**: `id`, `user_id` → users, `exercise`, `mark`, `timestamp`
