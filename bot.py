import requests
import json
import time
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Back, Style
import random
import os
import pyfiglet

# colorama
colorama.init(autoreset=True)

def print_welcome_message():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = pyfiglet.figlet_format("ZED", font="small")
    ascii_art1 = pyfiglet.figlet_format("FABRIKA CLAIMER", font="small")
    print(Fore.CYAN + ascii_art + Style.RESET_ALL)
    print(Fore.CYAN + ascii_art1 + Style.RESET_ALL)
    print(Fore.YELLOW + "t.me/zeedtek")
    print(Fore.CYAN + Style.BRIGHT + "---- FABRIKABOT ----")

def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def login_telegram(payload):
    url = "https://api.ffabrika.com/api/v1/auth/login-telegram"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
    }
    data = {"webAppData": {"payload": payload}}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['data']['accessToken']['value']
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Login failed: {str(e)}")
        return None

def get_profile(token):
    url = "https://api.ffabrika.com/api/v1/profile"
    headers = {"cookie": f"acc_uid={token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Failed to retrieve profile: {str(e)}")
        return None

def collect_factory_rewards(token):
    url = "https://api.ffabrika.com/api/v1/factories/my/rewards/collection"
    headers = {"cookie": f"acc_uid={token}"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 204:
            print(Fore.GREEN + "Rewards successfully collected.")
        else:
            print(Fore.YELLOW + f"Reward collection status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Failed to collect rewards: {str(e)}")

def assign_worker_tasks(token, task_type="longest"):
    url = "https://api.ffabrika.com/api/v1/factories/my/workers/tasks/assignment"
    headers = {
        "cookie": f"acc_uid={token}",
        "Content-Type": "application/json"
    }
    payload = {"type": task_type}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 204:
            print(Fore.GREEN + "Worker successfully assigned.")
        else:
            print(Fore.YELLOW + f"Task assignment status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Failed to assign worker tasks: {str(e)}")

def send_scores_request(token):
    url = "https://api.ffabrika.com/api/v1/scores"
    headers = {
        "Content-Type": "application/json",
        "cookie": f"acc_uid={token}"
    }
    
    count = random.randint(80, 150)
    data = {"count": count}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(Fore.GREEN + f"Taps {count} successful")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Failed to send request: {str(e)}")
        return None

def process_account(payload):
    token = login_telegram(payload)
    if not token:
        return
    
    profile = get_profile(token)
    if not profile:
        return
    
    print(Fore.CYAN + Style.BRIGHT + f"▬▬ USER NAME:  {profile['username']}")
    print(Fore.CYAN + Style.BRIGHT + f"▬▬▬ NAME: {profile['firstName']} {profile['lastName'] or ''}")
    print(Fore.GREEN + Style.BRIGHT + f"▬▬Status: {profile['status']}≽")
    print(Fore.CYAN + Style.BRIGHT + f"▬▬score: {profile['score']['total']}≽")
    print(Fore.CYAN + Style.BRIGHT + f"▬▬League: {profile['league']['name']}≽")
    print(Fore.CYAN + Style.BRIGHT + f"▬▬Energy: {profile['energy']['balance']}/{profile['energy']['limit']}≽")
    
    factory_data = profile.get('factory')
    if factory_data:
        print(Fore.CYAN + Style.BRIGHT + f"▬factory ID: {factory_data['id']}")
        print(Fore.WHITE + Style.BRIGHT + f"▬▬REWARDS : {factory_data['rewardCount']}")
        
        if factory_data['rewardCount'] > 0:
            collect_factory_rewards(token)
        else:
            print(Fore.YELLOW + Style.BRIGHT + "▬▬No rewards to collect.")
        
        if not factory_data['isPlanted'] and not factory_data['isDestroyed']:
            assign_worker_tasks(token)
        else:
            print(Fore.YELLOW + "Factory not available for tasks.")
    else:
        print(Fore.RED + "No factory data in profile.")
    
    while profile['energy']['balance'] > 0:
        print(Fore.WHITE + Style.BRIGHT + f"▬▬▬Remaining Energy▬▬▬ {profile['energy']['balance']}≽")
        response = send_scores_request(token)
        if response:
            profile = get_profile(token)
            if not profile:
                return
        else:
            print(Fore.RED + "Failed to send request. Stopping loop.")
            break
    
    print(Fore.GREEN + "Energy depleted, finished processing account\n")

def main():
    print_welcome_message()
    accounts = load_accounts()
    total_accounts = len(accounts)
    
    print(Fore.BLUE + Style.BRIGHT + f" ▬▬▬TOTAL ACCOUNTS: {total_accounts}≽")
    
    for i, payload in enumerate(accounts, 1):
        print(Fore.GREEN + Style.BRIGHT + f"▬▬▬ Processing account {i} of {total_accounts}≽")
        process_account(payload)
        if i < total_accounts:
            print(Fore.WHITE + Style.BRIGHT + "5 seconds to move to next account  ...")
            time.sleep(5)
    
    print(Fore.GREEN + "All accounts have been processed.")
    
    while True:
        target_time = datetime.now() + timedelta(days=0.01157)
        while datetime.now() < target_time:
            remaining_time = target_time - datetime.now()
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(Fore.YELLOW + f"\rTime remaining: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
            time.sleep(1)
        
        print(Fore.GREEN + "\nStarting process again...")
        main()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(Fore.RED + f"An error occurred: {str(e)}")
        print(Fore.YELLOW + "Continuing to the next task...")
