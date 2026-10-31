# main.py

from interfaces.cli.app import CLIApp

if __name__ == "__main__":
    try:
        app = CLIApp()
        app.run()
    except KeyboardInterrupt:
        print("\nEjecución cancelada por el usuario.")