from duckargs import process_args, generate_python_code

def main():
    try:
        print(generate_python_code(process_args()))
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
    
if __name__ == "__main__":
    main()
