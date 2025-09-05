from watchgod import run_process
from main import main
import asyncio

def start():
    asyncio.run(main())

if __name__ == "__main__":
    run_process('.', start)

