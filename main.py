import dictionary

if __name__ == "__main__":
    buffer = dictionary.Buffer()

    while True:
        word = input()
        print()
        entry = dictionary.search(word, buffer = buffer)
        
        if entry:
            print(entry)
        else:
            print("word not found")

        if input("Would you like to try another word? (y)es/(n)o?").lower()[0] != "y":
            exit(0)
