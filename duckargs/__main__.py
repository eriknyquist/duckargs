from duckargs import generate_python_code

def main():
    try:
        print(generate_python_code())
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
    
if __name__ == "__main__":
    main()
