import sqlite3
import os
from sqlite3 import Error
from colorama import Fore
from colorama import Style
from cryptography.fernet import Fernet

def main():
    database = r"/home/manjaro/Documents/Scripts/pwmanager.db"

    sql_create_accounts = """ CREATE TABLE IF NOT EXISTS accounts (
                                        id integer PRIMARY KEY,
                                        name text,
                                        username text,
                                        password text
                                    ); """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_accounts)
    else:
        print("Error! cannot create the database connection.")
        return

    # Initiates main menu/options
    choice(menu(), conn)

# Function to establish connection to database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

# Function to create main database table if it doesn't already exist
def create_table(conn, create_table_sql):

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

# Displays main menu
def menu():
    clear()
    print(Fore.CYAN + "PWManager" + Style.RESET_ALL)
    print("--------------------------------")
    print("Select one of the options below:")
    print("\n")
    print("1. Retrieve Account Password")
    print("2. Update Account Password")
    print("3. Add Account")
    print("4. Remove Account")
    print("5. List Accounts")
    print("6. Exit")
    print("\n")
    choice = input("Enter Choice: ")
    return choice

# Displays main options
def choice(option, conn):
    if option == '1':
        retrieveAccount(conn)
    elif option == '2':
        updateAccount(conn)
    elif option == '3':
        createAccount(conn)
    elif option == '4':
        removeAccount(conn)
    elif option == '5':
        c = conn.cursor()
        c.execute("SELECT name FROM accounts ORDER BY name")
        lname = c.fetchall()
        clear()
        print(Fore.CYAN + "Account Listing:"  + Style.RESET_ALL)
        print("--------------------------------")
        for names in lname:
            print(Fore.GREEN + names[0] + Style.RESET_ALL)
        returnMenu()
    elif option == '6':
        clear()
        return
    else:
        print("\n")
        print("No valid option selected.")
        print("Returning to main menu.")
        main()

# Function to retrieve an account/password
def retrieveAccount(conn):
    clear()
    print(Fore.CYAN + "Retrieving Account"  + Style.RESET_ALL)
    print("--------------------------------")
    name = input("Enter Account Name: ")

    try:
        c = conn.cursor()

        #Tests if account exists in database
        test = accountExists(conn, name)

        # If account exists, deletes account
        if test == True:
            c.execute("SELECT * FROM accounts WHERE name = ?", (name,))
            key = load_key()
            f = Fernet(key)
            rows = c.fetchall()

            clear()
            print(Fore.CYAN + name + " Account Information:"  + Style.RESET_ALL)
            print("--------------------------------")
            for row in rows:
                print(Fore.GREEN + "Username: " + row[2])
                pw = row[3]
                dpw = f.decrypt(pw).decode("utf-8")
                print("Password: " + dpw + Style.RESET_ALL)
                returnMenu()

        # If account doesn't exist, displays error
        else:
            print(Fore.RED + "No account exists under " + name + ". Names are case-sensitive." + Style.RESET_ALL)
            returnMenu()
    except sqlite3.Error as error:
        print("Failed to retrieve password.", error)

# Function to update an account/password
def updateAccount(conn):
    clear()
    print(Fore.CYAN + "Updating Account" + Style.RESET_ALL)
    print("--------------------------------")
    name = input("Enter Account Name: ")
    username = input("Enter Username: ")
    pw = input("Enter Password: ").encode()

    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(pw)

    try:
        c = conn.cursor()

        #Tests if account exists in database
        test = accountExists(conn, name)

        # If account exists, deletes account
        if test == True:
            c.execute("UPDATE accounts SET name = ?, username = ?, password = ? WHERE name = ?", (name, username, encrypted_message, name,))
            conn.commit()

            clear()
            print(Fore.GREEN + "Account " + name + " has been updated." + Style.RESET_ALL)
            returnMenu()

        # If account doesn't exist, displays error
        else:
            clear()
            print(Fore.RED + "No account exists under " + name + ". Names are case-sensitive." + Style.RESET_ALL)
            returnMenu()
    except sqlite3.Error as error:
        print("Failed to update account.", error)

# Function to create an account/password
def createAccount(conn):
    clear()
    print(Fore.CYAN + "Creating Account" + Style.RESET_ALL)
    print("--------------------------------")
    name = input("Enter Account Name: ")
    username = input("Enter Username: ")
    pw = input("Enter Password: ").encode()

    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(pw)

    try:
        c = conn.cursor()
        task = (name, username, encrypted_message)
        sql = ''' INSERT INTO accounts(name, username, password)
                  VALUES(?,?,?) '''
        c.execute(sql, task)
        conn.commit()

        clear()
        print(Fore.GREEN + "Account " + name + " has been created." + Style.RESET_ALL)
        returnMenu()
    except sqlite3.Error as error:
        print("Failed to create account.", error)

# Function to remove an account/password
def removeAccount(conn):
    clear()
    print(Fore.CYAN + "Removing Account" + Style.RESET_ALL)
    print("--------------------------------")
    name = input("Enter Account Name: ")

    try:
        c = conn.cursor()

        #Tests if account exists in database
        test = accountExists(conn, name)

        # If account exists, deletes account
        if test == True:
            c.execute("DELETE FROM accounts WHERE name = ?", (name,))
            conn.commit()

            clear()
            print(Fore.GREEN + "Account " + name + " has been deleted." + Style.RESET_ALL)
            returnMenu()

        # If account doesn't exist, displays error
        else:
            clear()
            print(Fore.RED + "No account exists under " + name + ". Names are case-sensitive." + Style.RESET_ALL)
            returnMenu()
    except sqlite3.Error as error:
        print("Failed to delete account.", error)  

# Lists options after running one of the main functions
def returnMenu():
    print("\n")
    print(Fore.CYAN + "Sub Menu" + Style.RESET_ALL)
    print("--------------------------------")
    print("Select one of the options below:")
    print("\n")
    print("1. Return to main menu")
    print("2. Exit")
    print("\n")
    choice = input("Enter Choice: ")
    if choice == '1':
        main()
    elif choice == '2':
        clear()
        return
    else:
        print("\n")
        print("No valid option selected.")
        returnMenu()

# Checks if account exists
def accountExists(conn, name):
        #Tests if account exists in database
        c = conn.cursor()
        c.execute("SELECT 1 FROM accounts WHERE name = ?", (name,))
        test = c.fetchone() is not None
        return test

# Use once to generate key for encryption/decryption
def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Loads key for encryption/decryption
def load_key():
    return open("key.key", "rb").read()

# Clears screen
def clear():
    os.system('clear')

# Initiates App 
if __name__ == '__main__':
    main()

    # Uncomment this once to create key for encryption/decryption
    #write_key()
