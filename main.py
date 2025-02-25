from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, SubmitField
from flask_wtf.recaptcha import RecaptchaField
from wtforms.validators import DataRequired
from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np

# Ключи reCAPTCHA
RECAPTCHA_PUBLIC_KEY = '6LfkMeIqAAAAAPhWMCeR7viSuB3QL8UYYKqu0rM9'  # Замените на ваш site key
RECAPTCHA_PRIVATE_KEY = '6LfkMeIqAAAAAOGfJWNeqZHxftJLngVlrhE1nS6p'  # Замените на ваш secret key

# Создаем Flask приложение
app = Flask(__name__)

# Секретный ключ Flask для работы с формами
app.config['SECRET_KEY'] = '6LfkMeIqAAAAAOGfJWNeqZHxftJLngVlrhE1nS6p'  # Установите свой секретный ключ
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfkMeIqAAAAAPhWMCeR7viSuB3QL8UYYKqu0rM9'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfkMeIqAAAAAOGfJWNeqZHxftJLngVlrhE1nS6p'


class UploadForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired()])
    scale = FloatField('Scale', default=1, validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Resize Image')


# Главная страница
@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        if 'image' in request.files:
            image = request.files['image']
            scale = form.scale.data

            # Открываем изображение и изменяем его размер
            img = Image.open(image)
            width, height = img.size
            img = img.resize((int(width * scale), int(height * scale)))

            # Сохраняем измененное изображение в папке static
            output_path = os.path.join('static', 'resized_image.png')
            img.save(output_path)

            # Генерация графиков распределения цветов
            create_color_histograms(image, 'static/original_histogram.png')  # Гистограмма исходного изображения
            create_color_histograms(output_path, 'static/resized_histogram.png')  # Гистограмма измененного изображения

            return redirect(url_for('show_image', filename='resized_image.png'))
    return render_template('index.html', form=form)


# Страница для отображения измененного изображения и графиков
@app.route('/image/<filename>')
def show_image(filename):
    return render_template('image.html', filename=filename)


# Функция для создания гистограммы распределения цветов
def create_color_histograms(image_path, output_path):
    img = Image.open(image_path)
    img = img.convert('RGB')

    # Преобразуем изображение в массив numpy для анализа
    img_array = np.array(img)

    # Распределение цветов по каналам
    r_hist, bins = np.histogram(img_array[:, :, 0], bins=256, range=(0, 255))
    g_hist, bins = np.histogram(img_array[:, :, 1], bins=256, range=(0, 255))
    b_hist, bins = np.histogram(img_array[:, :, 2], bins=256, range=(0, 255))

    # Строим график
    plt.figure(figsize=(10, 6))
    plt.title("Color Distribution")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.xlim(0, 255)

    # Рисуем гистограммы для каждого канала
    plt.plot(bins[:-1], b_hist, color='blue', alpha=0.6, label='Blue')
    plt.plot(bins[:-1], g_hist, color='green', alpha=0.6, label='Green')
    plt.plot(bins[:-1], r_hist, color='red', alpha=0.6, label='Red')

    # Добавляем легенду
    plt.legend()

    # Сохраняем график
    plt.savefig(output_path)
    plt.close()


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)