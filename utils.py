def name_validation(name: str) -> bool:
    if len(name.split()) != 4:
        return False

    name, surname, patronymic, group = name.split()

    return f"{name}{surname}{patronymic}".isalpha() and group.isalnum()
