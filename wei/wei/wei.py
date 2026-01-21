"""Guess My Number Game - A simple number guessing game."""

import random


def play_game():
    """Play the Guess My Number game."""
    print("=" * 40)
    print("  Welcome to Guess My Number!")
    print("=" * 40)
    print("\nI'm thinking of a number between 1 and 100.")
    print("Can you guess what it is?\n")

    secret_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10

    while attempts < max_attempts:
        remaining = max_attempts - attempts
        print(f"Attempts remaining: {remaining}")

        try:
            guess = int(input("Enter your guess: "))
        except ValueError:
            print("Please enter a valid number.\n")
            continue

        attempts += 1

        if guess < 1 or guess > 100:
            print("Please guess a number between 1 and 100.\n")
            attempts -= 1  # Don't count invalid range as an attempt
            continue

        if guess < secret_number:
            print("Too low! Try a higher number.\n")
        elif guess > secret_number:
            print("Too high! Try a lower number.\n")
        else:
            print(f"\n?? Congratulations! You guessed it!")
            print(f"The number was {secret_number}.")
            print(f"You got it in {attempts} attempt(s)!\n")
            return True

    print(f"\n?? Game Over! You ran out of attempts.")
    print(f"The secret number was {secret_number}.\n")
    return False


def main():
    """Main function to run the game with replay option."""
    while True:
        play_game()
        play_again = input("Would you like to play again? (yes/no): ").strip().lower()
        if play_again not in ("yes", "y"):
            print("\nThanks for playing! Goodbye! ??\n")
            break
        print("\n")


if __name__ == "__main__":
    main()
