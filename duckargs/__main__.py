from duckargs import process_args, generate_python_code

def main():
    print(generate_python_code(process_args()))
    
if __name__ == "__main__":
    main()
