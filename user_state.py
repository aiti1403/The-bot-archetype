# Управление состоянием пользователя
class UserState:
    def __init__(self):
        self.users = {}
    
    def get_user_state(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = {
                'state': 0,  # 0 - начало, 1 - отвечает на вопросы, 2 - завершил
                'current_question': 0,
                'answers': {},
                'archetype_scores': {
                    'Принц/Принцесса': 0,
                    'Бродяга/Дрянная девчонка': 0,
                    'Трикстер/Жрица': 0,
                    'Черный маг/Ведьма': 0,
                    'Герой/Амазонка': 0,
                    'Злодей/Охотница': 0,
                    'Хозяин/Хозяйка': 0,
                    'Людоед/Ужасная Мать': 0
                }
            }
        return self.users[user_id]
    
    def update_user_state(self, user_id, state=None, question=None):
        user_data = self.get_user_state(user_id)
        if state is not None:
            user_data['state'] = state
        if question is not None:
            user_data['current_question'] = question
        return user_data
    
    def record_answer(self, user_id, question_index, answer_index):
        user_data = self.get_user_state(user_id)
        user_data['answers'][question_index] = answer_index
        
        # Обновляем счет архетипа
        from questions import QUESTIONS
        archetype = QUESTIONS[question_index]['archetypes'][answer_index]
        user_data['archetype_scores'][archetype] += 1
        
        return user_data
    
    def get_dominant_archetype(self, user_id):
        user_data = self.get_user_state(user_id)
        scores = user_data['archetype_scores']
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def reset_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
