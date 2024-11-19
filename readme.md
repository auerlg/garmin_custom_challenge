Playing around with garminconnect to create custom challenges, using the **"movingDuration"** variable to count active minutes.
Optionally **Training load** or **other variables** can be used for other ranking or other activity type.

Usage, prerequisites:
1. python3, pip installed
2. create **.env** file in the project directory in the following format:

```console
GARMIN_USERNAME=my_email@example.com
GARMIN_PASSWORD=my_secure_password
```
3. run with date parameter
```console
pip install garminconnect
python3 strength_v2.py 2024-11-17
```
strength_v2 will display the total active minutes spent on strength training since the supplied date.