import time
import schedule
from modules.scheduled_tasks import run_all_scheduled_tasks
from utils.config import CONFIG

def main():
    """
    Main function to set up and run the scheduled tasks for WOTSON.
    """
    try:
        run_interval = int(CONFIG.get("run_interval_hours", 2))
    except (ValueError, TypeError):
        print("Warning: 'run_interval_hours' in config is invalid. Defaulting to 2 hours.")
        run_interval = 2

    print("--- WOTSON Scheduler Initialized ---")
    print(f"Running all tasks every {run_interval} hours.")
    print("Press Ctrl+C to stop the scheduler.")

    # Run once immediately at startup for testing
    run_all_scheduled_tasks()

    # Schedule the tasks to run periodically
    schedule.every(run_interval).hours.do(run_all_scheduled_tasks)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # To run this, you first need to install the dependencies:
    # pip install -r requirements.txt
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
    except FileNotFoundError as e:
        print(f"\nError: {e}. Make sure the configuration and module paths are correct.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}") 