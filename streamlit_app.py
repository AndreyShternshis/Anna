import streamlit as st
import json
import os
import matplotlib.pyplot as plt
import numpy as np

FILENAME = "entries.json"

# --- Data handling ---
def load_entries():
    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            return json.load(f)
    return {}

def save_entries(entries):
    with open(FILENAME, 'w') as f:
        json.dump(entries, f, indent=2)

# --- Submit form ---
def submit_entry():
    name = st.session_state['name_input'].strip()
    rating_text = st.session_state['rating_input'].strip()
    comment = st.session_state['comment_input'].strip()

    if not name:
        st.error("Имя не может быть пустым.")
        return

    rating = None
    if rating_text:
        try:
            rating = int(rating_text)
            if not (0 <= rating <= 10):
                raise ValueError
        except ValueError:
            st.error("Оценка должна быть числом от 0 до 10 или оставьте пустым.")
            return

    entries = load_entries()

    if rating == 0:
        if name in entries:
            del entries[name]
            save_entries(entries)
            st.success(f"Удалена запись для '{name}' (оценка 0).")
        else:
            st.warning(f"Нет записи для '{name}' для удаления.")
        return

    if name not in entries:
        entries[name] = {'rating': rating or 0, 'comments': []}

    if rating is not None:
        entries[name]['rating'] = rating

    if comment:
        entries[name]['comments'].append(comment)

    save_entries(entries)
    st.success(f"Обновлена запись для '{name}'.")

    st.session_state['name_input'] = ""
    st.session_state['rating_input'] = ""
    st.session_state['comment_input'] = ""

# --- Plot ratings ---
def plot_race():
    entries = load_entries()
    if not entries:
        st.warning("Нет записей для отображения.")
        return

    sorted_items = sorted(entries.items(), key=lambda x: x[1]['rating'], reverse=True)
    names = [item[0] for item in sorted_items]
    ratings = np.array([item[1]['rating'] for item in sorted_items])

    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.3)))
    y_positions = list(reversed(range(len(names))))
    norm_ratings = (ratings - 1) / 9
    cmap = plt.get_cmap('RdYlGn')
    colors = cmap(norm_ratings)

    ax.scatter(ratings, y_positions, s=100, c=colors)
    ax.set_yticks([])
    for y, (name, rating) in zip(y_positions, zip(names, ratings)):
        ax.text(rating + 0.1, y, name, va='center', fontsize=10)

    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-1, len(names))
    ax.set_xlabel("Оценка")
    ax.grid(axis='x')
    st.pyplot(fig)

# --- Show comments ---
def show_comments(selected_name):
    entries = load_entries()
    if selected_name in entries:
        rating = entries[selected_name]['rating']
        comments = entries[selected_name].get('comments', [])
        st.markdown(f"**Комментарии для {selected_name} (оценка: {rating}):**")
        if comments:
            for i, c in enumerate(comments, 1):
                st.markdown(f"{i}. {c}")
        else:
            st.write("Пока нет комментариев.")
    else:
        st.warning("Нет данных для выбранного имени.")

# --- UI ---
st.set_page_config(page_title="Feedback Race App", layout="centered")
st.title("💬 Все Анины женихи")

# --- Menu buttons ---
tab1, tab2, tab3 = st.tabs(["🟢 Я Аня", "🏁 гонка женихов", "📋 Да кто это вообще такой?"])

with tab1:
    st.subheader("Добавить или обновить")
    st.text_input("Имя", key='name_input')
    st.text_input("Оценка (0–10, опционально)", key='rating_input')
    st.text_area("Комментарий", key='comment_input')
    st.button("Обновить", on_click=submit_entry)

with tab2:
    st.subheader("Гонка по рейтингу")
    plot_race()

with tab3:
    st.subheader("Комментарии")
    entries = load_entries()
    if entries:
        name_list = sorted(entries.keys())
        selected_name = st.selectbox("Выберите имя", name_list)
        if selected_name:
            show_comments(selected_name)
    else:
        st.info("Нет доступных записей.")
