import json


class FaqDataHandler:
    def __init__(self):
        pass

    @staticmethod
    def get_questions(file_name: str) -> list[str]:
        with open(file_name, 'r', encoding='utf-8') as f:
            table = json.load(f)
            return list(table.keys())
        
    @staticmethod
    def get_answer(file_name: str, question: str) -> str:
        with open(file_name, 'r', encoding='utf-8') as f:
            table = json.load(f)
            return table.get(question, '')
        
    @staticmethod
    def get_all_data(file_name: str) -> dict[str, str]:
        with open(file_name, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    @staticmethod
    def add_question(file_name: str, question: str, answer: str):
        with open(file_name, 'r', encoding='utf-8') as f:
            table = json.load(f)
            table[question] = answer
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(table, f, ensure_ascii=False, indent=4)
    
    @staticmethod
    def remove_question(file_name: str, question: str):
        with open(file_name, 'r', encoding='utf-8') as f:
            table = json.load(f)
            del table[question]
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(table, f, ensure_ascii=False, indent=4)
    
    @staticmethod
    def edit_question(file_name: str, question: str, new_question: str):
        with open(file_name, 'r', encoding='utf-8') as f:
            table = json.load(f)
            table[new_question] = table[question]
            del table[question]
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(table, f, ensure_ascii=False, indent=4)
    
    @staticmethod
    def edit_answer(file_name: str, question: str, new_answer: str):
        with open(file_name, 'r', encoding='utf-8') as f:
            table = json.load(f)
            table[question] = new_answer
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(table, f, ensure_ascii=False, indent=4)
            