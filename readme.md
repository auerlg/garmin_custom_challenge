### Playing around with garminconnect to create custom challenges, using the **"movingDuration"** variable to count active minutes. Optionally **Training load** or **other variables** can be used for other ranking or other activity type.

### Usage, prerequisites:
1. python3, pip installed
2. create **.env** file in the project directory in the following format:

```console
GARMIN_USERNAME=my_email@example.com
GARMIN_PASSWORD=my_secure_password
```
3. run with date parameter
```console
pip install garminconnect
python3 multi-counter.py 2024-11-17
```
strength_v2 will display the total active minutes spent on strength training since the supplied date.

example output:
```console
Logged in successfully!
Fetched activities successfully!
Total moving duration for strength training activities since 2024-11-01: 67.77 minutes
Total PUSH_UP reps since 2024-11-01: 140
Total PULL_UP reps since 2024-11-01: 7
```

### Alternative to the python client in go: https://github.com/abrander/garmin-connect