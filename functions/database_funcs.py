import os

import psycopg2


def ConnectToDataBase():
    connection = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        port=int(os.getenv("PORT")),
        host=os.getenv("HOST")
    )
    return connection


def create_tables_from_db():
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS questions (
            id serial PRIMARY KEY,
            question_text varchar NOT NULL,
            admin_id int NOT NULL,
            publish_date timestamp NOT NULL
        );
            """)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS admins (
            id serial PRIMARY KEY,
            telegram_id bigint NOT NULL,
            name varchar NOT NULL
        );
            """)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS choice (
            id serial PRIMARY KEY,
            choice_text varchar NOT NULL,
            votes integer NOT NULL,
            question_id bigint NOT NULL
        );
            """
        )
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS user_statistics (
            id serial PRIMARY KEY,
            telegram_id bigint NOT NULL,
            question_id bigint NOT NULL,
            choice_id integer NOT NULL
        );
            """
        )
    connection.commit()
    connection.close()


def add_admin_to_db(telegram_id: int, name: str):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("SELECT admins.telegram_id FROM admins WHERE admins.telegram_id = (%s)", (telegram_id,))
        admins_db = cursor.fetchone()
        if not admins_db:
            cursor.execute("INSERT INTO admins (telegram_id, name) VALUES ((%s), (%s))", (telegram_id, name))
    connection.commit()
    connection.close()


def get_admin_id(telegram_id):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM admins WHERE telegram_id = (%s)", (telegram_id,))
        admin_id = cursor.fetchone()
    connection.commit()
    connection.close()
    return admin_id[0]


def add_question_to_db(question_text, telegram_id, publish_date):
    connection = ConnectToDataBase()
    admin_id = get_admin_id(telegram_id)
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO questions (question_text, admin_id, publish_date) VALUES ((%s),(%s),(%s))",
            (question_text, admin_id, publish_date)
        )
    connection.commit()
    connection.close()


def get_id_last_question_db():
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(id) FROM questions")
        id_last = cursor.fetchone()
    connection.commit()
    connection.close()
    return id_last[0]


def add_choices_to_db(choice_text, votes, question_id):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO choice (choice_text, votes, question_id) VALUES ((%s),(%s),(%s))",
            (choice_text, votes, question_id)
        )
    connection.commit()
    connection.close()


def get_questions_answered_user_db(telegram_id, for_stats=False):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT user_statistics.question_id, questions.question_text, choice.choice_text FROM user_statistics 
            JOIN questions on questions.id = user_statistics.question_id
            JOIN choice on choice.id = user_statistics.choice_id
            WHERE telegram_id = (%s)
            """, (telegram_id, ))
        if for_stats:
            questions = [q[1:] for q in cursor.fetchall()]
        else:
            questions = [q[0] for q in cursor.fetchall()]
    connection.commit()
    connection.close()
    return questions


def get_questions_for_user_db(answered_questions=None):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        if answered_questions:
            cursor.execute("SELECT question_id FROM choice WHERE question_id > (%s)", (max(answered_questions),))
            questions = list(set([q[0] for q in cursor.fetchall()]))
        else:
            cursor.execute("SELECT question_id FROM choice")
            questions = list(set([q[0] for q in cursor.fetchall()]))
    connection.commit()
    connection.close()
    return questions


def last_answered_question_db(telegram_id):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("SELECT question_id FROM user_statistics WHERE telegram_id = (%s)", (telegram_id,))
        questions = [q[0] for q in cursor.fetchall()]
    connection.commit()
    connection.close()
    if questions:
        return [len(questions), questions[-1]]
    return [0, 0]


def get_current_question_db(last):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT choice.question_id, questions.question_text FROM choice
        JOIN questions on questions.id = choice.question_id
        WHERE choice.question_id > (%s)
        ORDER BY questions.id""", (last,))
        question = cursor.fetchone()
    connection.commit()
    connection.close()
    if question:
        dict_question = dict(id=question[0], text=question[1])
        return dict_question
    return None


def get_current_choices(question_id):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, choice_text FROM choice WHERE question_id = (%s)", (question_id,))
        choices = cursor.fetchall()
    connection.commit()
    connection.close()
    # dict_choices = {}
    string_choices = []
    for choice in sorted(choices):
        string_choices.append(f'{choice[0]}, {choice[1]}')
    return string_choices


def add_user_vote_db(choice_id, telegram_id):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("""
        UPDATE choice
        SET votes = votes + 1
        WHERE id = (%s)
        """, (choice_id, ))
        cursor.execute("SELECT question_id FROM choice WHERE id = (%s)", (choice_id,))
        question_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO user_statistics (telegram_id, question_id, choice_id) VALUES ((%s), (%s), (%s))",
            (telegram_id, question_id, choice_id)
        )
    connection.commit()
    connection.close()


def get_all_stats_db() -> str:
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT questions.id, questions.question_text, sum(choice.votes) as cnt_votes FROM questions
            JOIN choice on choice.question_id = questions.id
            GROUP BY questions.id
            ORDER BY questions.id
            """
        )
        id_text_votes = cursor.fetchall()
        choice_votes = []
        for i, q in enumerate(id_text_votes):
            cursor.execute(
                """
                SELECT choice.choice_text, choice.votes FROM choice
                JOIN questions on questions.id = choice.question_id
                WHERE choice.question_id = (%s)
                ORDER BY choice.id
                """,
                (q[0], )
            )
            choice_votes.append(cursor.fetchall())
    connection.commit()
    connection.close()
    text_list = []
    for i, q in enumerate(id_text_votes):
        choices = []
        for j in choice_votes[i]:
            choices.append(f'{j[0]} -- {j[1]}')
        str_choices = "\n- ".join(choices)
        text_list.append(
            f'🔹 {i+1}. {q[1]}\nПринявших участие: {q[2]}\nОтветы:\n- {str_choices}'
        )
    return "\n\n".join(text_list)


def get_all_questions_db(first_id=None, last_id=None):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        if first_id and not last_id:
            cursor.execute("SELECT id, question_text FROM questions WHERE id >= (%s)", (first_id, ))
            result = cursor.fetchall()
        if last_id and not first_id:
            cursor.execute("SELECT id, question_text FROM questions WHERE id <= (%s)", (last_id,))
            result = cursor.fetchall()
        if first_id and last_id:
            cursor.execute("SELECT id, question_text FROM questions WHERE id <= (%s)", (last_id,))
            result = cursor.fetchall()
        if not first_id and not last_id:
            cursor.execute("SELECT id, question_text FROM questions")
            result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result


def delete_question_by_id_db(question_id):
    connection = ConnectToDataBase()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM user_statistics WHERE question_id = (%s)", (question_id, ))
        cursor.execute("DELETE FROM choice WHERE question_id = (%s)", (question_id, ))
        cursor.execute("DELETE FROM questions WHERE id = (%s)", (question_id, ))
    connection.commit()
    connection.close()