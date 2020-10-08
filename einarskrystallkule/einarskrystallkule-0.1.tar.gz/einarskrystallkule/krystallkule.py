import random

def spaa(question: str) -> str:
    """Responds to a question asked by the user

    Args:
        question (str): Question from the user

    Returns:
        str: The crystal ball's response
    """

    possible_responses = ["Ja", "Nei", "Kanskje", "Vet ikke", "Du får vente og se", "Patience, young padawan", "Helt klart"]

    return random.sample(possible_responses, 1)


if __name__ == "__main__":
    print(spaa("Hva skjer"))
