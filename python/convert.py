def create_unique_user_list(input_filename, output_filename):
    # Множество для хранения уникальных имен пользователей
    unique_users = set()
    
    with open(input_filename, 'r') as input_file:
        for line in input_file:
            username, _ = line.strip().split(',')
            unique_users.add(username)
    
    with open(output_filename, 'w') as output_file:
        for username in sorted(unique_users):
            output_file.write(f"{username},")

input_filename = "metadata.bin"
output_filename = 'github-accounts.txt' 

create_unique_user_list(input_filename, output_filename)